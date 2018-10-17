//File containing main entry point

#include <Arduino_FreeRTOS.h>
#include <semphr.h>

#include "comms_protocol.h"
#include "config.h"
#include "data_buffers.h"

#include<Wire.h>
extern "C" { 
#include "utility/twi.h"  // from Wire library, so we can do bus scanning
}

#define NUM_SAMPLES 20
#define TCAADDR 0x70

void TaskSendMessage(void *pvParameters);
void TaskFormatMessage(void * pvParameters);
void TaskReadData(void *pvParameters);

void establish_connection();
void transmit_data_from_buffer();
void terminate_connection();
void update_power_readings();

void send_16bit(uint16_t data);
void tcaselect(uint8_t i);

//////////////////////////////////////////////
//    CONSTANTS                             //
//////////////////////////////////////////////

// Constants for MPU Reading
const int FLEXPIN = 11;
const int MPU = 0x68;

// Constants for power reading
const int SENSOR_PIN_A0 = A0;   // Input pin for measuring Vout from INA169
const int SENSOR_PIN_A1 = A1;   // Input pin for measuring Vout from voltage divider
const float RS = 0.1;           // Shunt resistor value (in ohms) for INA169
const float VOLTAGE_REF = 5.0;  // Reference voltage for analog read, //5.126 <-- voltage regulator
const float R1 = 22000.0;       // Resistor 22k ohms (10% tolerance)
const float R2 = 22000.0;       // Resistor 22k ohms with 20% tolerance from R1 26888.889/25545.455/20431 with 5v

//////////////////////////////////////////////
//    GLOBAL VARIABLES                      //
//////////////////////////////////////////////

// Main message buffer to store formatted messages to send to PI
cbuffer_t msg_buffer;
// Semaphore to control access to main message buffer
SemaphoreHandle_t xMsgBuffSemaphore;

// Global Variables for power reading
int16_t power_data[4];                // Power data to be sent as 16 bit integers
uint8_t sample_count = 0;             // Current sample number
int16_t sensorValueA0 = 0;            // Variable to store value from analog read
int16_t sensorValueA1 = 0;            // Variable to store value from analog read/sum of samples taken
float voltageOut = 0.0;               // Calculated Voltage Out value, Vout = Vin * R2/(R1+R2)
float voltageIn = 0.0;                // Calculated Voltage In Source value
float current = 0.0;                  // Calculated current value
float totalCurrent = 0.0;             // Calculated Total current value
float avgAmp = 0.0;                   // Calculated avgAmp
float ampHr = 0.0;                    // Calculated amp-hour
float power = 0.0;                    // Calculated power value
float lastPower = 0.0;                // Previous power value
float energy = 0.0;                   // Calculated energy value
float elapsedTime = 0.0;

void setup() {
  //Initialize mpu
  pinMode(FLEXPIN, INPUT);
//  Wire.begin();
//  tcaselect(0);
//  Wire.beginTransmission(MPU);
//  Wire.write(0x6B); 
//  Wire.write(0);    
//  Wire.endTransmission(true);
//  tcaselect(1);
//  Wire.beginTransmission(MPU);
//  Wire.write(0x6B); 
//  Wire.write(0);    
//  Wire.endTransmission(true);
//  tcaselect(2);
//  Wire.beginTransmission(MPU);
//  Wire.write(0x6B); 
//  Wire.write(0);    
//  Wire.endTransmission(true);
//  tcaselect(3);
//  Wire.beginTransmission(MPU);
//  Wire.write(0x6B); 
//  Wire.write(0);    
//  Wire.endTransmission(true);
  // Initialize serial communication - 115200 bps,8 Data, 1 Stop, 0 Parity
  // Temporarily using Serial for debugging, will move over to Serial
  if (USB_DEBUG_MODE) {
    Serial.begin(115200, SERIAL_8N1);
  }
  Serial.begin(115200, SERIAL_8N1);

  /*
   * Initialize semaphores
   */
  if ( xMsgBuffSemaphore == NULL ) {
    xMsgBuffSemaphore = xSemaphoreCreateMutex(); 
    if ( ( xMsgBuffSemaphore ) != NULL ) {
      xSemaphoreGive( ( xMsgBuffSemaphore ) );
    }
  } 

  /*
   *  Initialize tasks
   */
  xTaskCreate(
    TaskSendMessage,
    (const portCHAR *) "SendMessage",
    STACK_SIZE,
    NULL,
    1,
    NULL
    );
    
  xTaskCreate(
    TaskReadData,
    (const portCHAR *) "ReadData",
    STACK_SIZE,
    NULL,
    2,
    NULL
    );
}

//////////////////////////////////////////////
//    HELPER FUNCTIONS                      //
//////////////////////////////////////////////

/*
 * Break 16 bit data into 2 8 bit parts, less significant is sent first
 * e.g data = 0xABCD - CD is transmitted first, followed by AB
 */
 void send_16bit(uint16_t data) {
  Serial.write(data);
  Serial.write(data >> 8);
 }
/*
 * Select which channelt to read the data from
 */
void tcaselect(uint8_t i) {
  if (i > 7) return;
 
  Wire.beginTransmission(TCAADDR);
  Wire.write(1 << i);
  Wire.endTransmission();  
}

/* 
* Initiate communication with RPi 
*/
void establish_connection() {
  uint8_t received_byte = NONE;
  uint16_t resend_timer = 0;
  Serial.write(SYNC);
  if (USB_DEBUG_MODE) {
    Serial.println(SYNC);
  }
  while (received_byte != ACK) {
    // Wait until response received from RPi
    // TODO - add time out
    while(!Serial.available()) {
      if (resend_timer == 1000) {
        Serial.write(SYNC); 
        resend_timer = 0;       
      } else {
        resend_timer++;
      }
    }
    // -48 since serial monitor/pi sends ascii characters
    received_byte = Serial.read() - 48;
    if (USB_DEBUG_MODE) {
      Serial.println(received_byte);
    }
  }
  Serial.write(SYNC_ACK);
  if (USB_DEBUG_MODE) {
    Serial.println(SYNC_ACK);
  } 
}

/* 
* Transfer data to RPi
*/
void transmit_data_from_buffer() {

  uint8_t received_byte = NONE;
  // Transmit data
  if ( xSemaphoreTake( xMsgBuffSemaphore, ( TickType_t ) 5 ) == pdTRUE ) {
    uint8_t *current_msg_ptr =  msg_buffer.data_buffer[msg_buffer.strt];
    while (received_byte != ACK) {
      //Transmit data
//       for(int i = 0; i < MSG_LEN; i++ ) {
//         send_16bit(current_msg_ptr[i]);
//          if (USB_DEBUG_MODE){
//            Serial.println(current_msg_ptr[i]);
//          } 
//       }
      Serial.write(current_msg_ptr, MSG_LEN);
      
      // Wait for reponse from RPi
      while(!Serial.available()) {};
      received_byte = Serial.read() - 48;
    }
    //update buffer state and allow current data to be overwritten
    msg_buffer.buff_size_remaining++;
    msg_buffer.strt++;
    if (msg_buffer.strt >= RAW_BUFF_SIZE) {
          msg_buffer.strt = 0;
    }
    xSemaphoreGive( xMsgBuffSemaphore );
  }
}

/* 
* Terminate communication with RPi
*/
void terminate_connection(){
  uint8_t received_byte = NONE;
  Serial.write(FIN);
  if (USB_DEBUG_MODE) {
    Serial.println(FIN);
  }
  while (received_byte != FIN) {
    // Wait until response received from RPi
    // TODO - add time out
    while(!Serial.available()) {};
    received_byte = Serial.read() - 48;
  }
  Serial.write(ACK);
  if (USB_DEBUG_MODE) {
    Serial.println(ACK);
  }
  received_byte = NONE;
}

/*
* Updates the power readings
*/
void update_power_readings() {
    if (sample_count < NUM_SAMPLES) {
      sensorValueA0 += analogRead(SENSOR_PIN_A0);
      sensorValueA1 += analogRead(SENSOR_PIN_A1);
      sample_count++;
    } else {
      // Actual voltage calibration: 
      // 2.73v 5.47v analogRead: 560
      // 1 is equivalent to 2.73/560=4.875mv
      // Vout = (4.875*sample)/1000
      // Actual battery voltage = (2*Vout)
      // Remap the ADC value into a voltage number
      sensorValueA0 = (sensorValueA0 / (float)NUM_SAMPLES * 4.875) / 1024.0;
      voltageOut = (sensorValueA1 / (float)NUM_SAMPLES * 4.875) / 1024.0;

      // Calculate Vin from Vout and two resistor
      // Battery V = 5.224, Voltage across resistor = 2.608
      // division factor = 2.001533742331288343558282208589
      voltageIn = voltageOut * 2;

      // Current value
      // Following the equation given by the INA169 datasheet to
      // determine the current flowing through RS. Assume RL = 10k
      // Is = (Vout x 1k) / (RS x RL)
      current = (sensorValueA0 / (RS * 10.0));
      totalCurrent = (totalCurrent + current * 1000) ;
      avgAmp = totalCurrent / elapsedTime;
      ampHr = (avgAmp * elapsedTime) / 3600; //mAh
      
      // Power value
      power = current * voltageIn;
      
      // Energy value
      if (power != 0) {
        energy = (power * elapsedTime) / 3600;
      }

      power_data[0] = current * 100;
      power_data[1] = power * 100;
      power_data[2] = energy * 100;
      power_data[3] = voltageIn * 100;

      sample_count = 0;
      sensorValueA0 = 0;
      sensorValueA1 = 0;
    }
}



//////////////////////////////////////////////
//          MAIN TASKS                      //
//////////////////////////////////////////////

void TaskSendMessage(void *pvParameters) {
  const TickType_t xDelay = SEND_DELAY / portTICK_PERIOD_MS;
  TickType_t xLastWakeTime;
  xLastWakeTime = xTaskGetTickCount();
  
  for(;;) {
    establish_connection();
    transmit_data_from_buffer();
    terminate_connection();
    //Sleep until next scheduled time
    vTaskDelayUntil(&xLastWakeTime, xDelay);
  }
}

void TaskReadData(void *pvParameters) {
  const TickType_t xDelay = READ_DATA_DELAY / portTICK_PERIOD_MS;
  TickType_t xLastWakeTime;
  xLastWakeTime = xTaskGetTickCount();
  for(;;) {
    update_power_readings(); //-METHOD 1
    if ( xSemaphoreTake( xMsgBuffSemaphore, ( TickType_t ) 5 ) == pdTRUE ) {
      if (msg_buffer.buff_size_remaining > 0) {
        uint8_t *current_msg_ptr =  msg_buffer.data_buffer[msg_buffer.bck];
        uint8_t checksum = 0;
        int16_t msg_buffer_index = 0;
        for (int i = 0; i < MPU_COUNT; i++) {
          // tcaselect(i);
          // Wire.beginTransmission(MPU);
          // Wire.write(0x3B);  
          // Wire.endTransmission(false);
          // Wire.requestFrom(MPU,12,true);  

          /* SENSOR IDs
           * j = 0 - 2 : AcX,Y,Z
           * j = 3     : Tmp
           * j = 4 - 6 : GyX,Y,Z
           */
            for (int j = 0; j < SENSOR_PER_MPU; j++) {
              int16_t data = j + 1;
              //int16_t data = Wire.read()<<8|Wire.read();
              if (j != 3) {
                uint8_t lsb = (data & 0x00FF);
                uint8_t msb = (data & 0xFF00) >> 8;
                //LSB is sent first, followed by MSB
                checksum ^= lsb;
                current_msg_ptr[msg_buffer_index++] = lsb;
                checksum ^= msb;
                current_msg_ptr[msg_buffer_index++] = msb;
              }
            }
          }
        int16_t data = 27;
        uint8_t lsb = (data & 0x00FF);
        uint8_t msb = (data & 0xFF00) >> 8;
        checksum ^= lsb;
        current_msg_ptr[msg_buffer_index++] = lsb;
        checksum ^= msb;
        current_msg_ptr[msg_buffer_index++] = msb;
        //int16_t Flex = digitalRead(FLEXPIN);
        //checksum ^= 0;
        //current_msg_ptr[msg_buffer_index++] = Flex;

        //Get power readings - METHOD 1
        for(int k = 0; k < 4; k++) {
          int16_t data = power_data[k];
          uint8_t lsb = (data & 0x00FF);
          uint8_t msb = (data & 0xFF00) >> 8;
          checksum ^= lsb;
          current_msg_ptr[msg_buffer_index++] = lsb;
          checksum ^= msb;
          current_msg_ptr[msg_buffer_index++] = msb;
        }
        
        //METHOD 2
        // if (sample_count < NUM_SAMPLES) {
        //   sensorValueA0 += analogRead(SENSOR_PIN_A0);
        //   sensorValueA1 += analogRead(SENSOR_PIN_A1);
        //   sample_count++;
        // } else {
        //   // Store value of sensor A0
        //   uint8_t lsb = (sensorValueA0 & 0x00FF);
        //   uint8_t msb = (sensorValueA0 & 0xFF00) >> 8;
        //   //LSB is sent first, followed by MSB
        //   checksum ^= lsb;
        //   current_msg_ptr[msg_buffer_index++] = lsb;
        //   checksum ^= msb;
        //   current_msg_ptr[msg_buffer_index++] = msb;

        //   // Store value of sensor A1
        //   uint8_t lsb = (sensorValueA1 & 0x00FF);
        //   uint8_t msb = (sensorValueA1 & 0xFF00) >> 8;
        //   //LSB is sent first, followed by MSB
        //   checksum ^= lsb;
        //   current_msg_ptr[msg_buffer_index++] = lsb;
        //   checksum ^= msb;
        //   current_msg_ptr[msg_buffer_index++] = msb;

        // }


        current_msg_ptr[msg_buffer_index] = checksum;
        //update buffer state and allow current data to be overwritten
        msg_buffer.buff_size_remaining--;
        msg_buffer.bck++;
        if (msg_buffer.bck >= RAW_BUFF_SIZE) {
          msg_buffer.bck = 0;
        }
      }
      xSemaphoreGive( xMsgBuffSemaphore );
    }
    vTaskDelayUntil(&xLastWakeTime, xDelay);
  }
}

void loop() {
  // put your main code here, to run repeatedly:

}
