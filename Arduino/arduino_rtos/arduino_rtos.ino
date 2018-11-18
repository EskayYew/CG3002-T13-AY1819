//File containing main entry point

#include <Arduino_FreeRTOS.h>
#include <semphr.h>
#include <avr/power.h>

#include "comms_protocol.h"
#include "config.h"
#include "data_buffers.h"

#include<Wire.h>
extern "C" { 
#include "utility/twi.h"  // from Wire library, so we can do bus scanning
}

#define NUM_SAMPLES 10
#define TCAADDR 0x70

#define power_usart3_disable() (PRR1 |= (uint8_t)(1 << PRUSART3))

////////////////////////////////////////////////////////
//    FUNCTION PROTOTYPES                             //
////////////////////////////////////////////////////////

void TaskSendMessage(void *pvParameters);
void TaskFormatMessage(void * pvParameters);
void TaskReadData(void *pvParameters);

void establish_connection();
void transmit_data_from_buffer();
void terminate_connection();
void update_power_readings();

void disable_unused_features();
void tcaselect(uint8_t i);

//////////////////////////////////////////////
//    CONSTANTS                             //
//////////////////////////////////////////////

// Constants for MPU Reading
const int FLEXPIN = 31;
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

// Connection status variables
bool connection_established = false;

// Global Variables for power reading
int16_t power_data[4];                // Power data to be sent as 16 bit integers
uint8_t sample_count = 0;             // Current sample number
float sensorValueA0 = 0;              // Variable to store value from analog read
float sensorValueA1 = 0;              // Variable to store value from analog read/sum of samples taken
float voltageOut = 0.0;               // Calculated Voltage Out value, Vout = Vin * R2/(R1+R2)
float voltageIn = 0.0;                // Calculated Voltage In Source value
float current = 0.0;                  // Calculated current value
float power = 0.0;                    // Calculated power value
float energy = 0.0;                   // Calculated energy value
float elapsedTime = 0.0;
unsigned long prevTime = 0;
unsigned long currTime = 0;

void setup() {
  //pinAsInput(FLEXPIN);
  disable_unused_features();
  pinMode(FLEXPIN, INPUT);
  //Initialize mpu
  Wire.begin();
  Wire.setClock(400000);
  tcaselect(0);
  Wire.beginTransmission(MPU);
  Wire.write(0x6B); 
  Wire.write(0);    
  Wire.endTransmission(true);
  tcaselect(6);
  Wire.beginTransmission(MPU);
  Wire.write(0x6B); 
  Wire.write(0);    
  Wire.endTransmission(true);
  tcaselect(7);
  Wire.beginTransmission(MPU);
  Wire.write(0x6B); 
  Wire.write(0);    
  Wire.endTransmission(true);

  // Initialize serial communication - 115200 bps,8 Data, 1 Stop, 0 Parity
  Serial1.begin(115200, SERIAL_8N1);

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
    2,
    NULL
    );
    
  xTaskCreate(
    TaskReadData,
    (const portCHAR *) "ReadData",
    STACK_SIZE,
    NULL,
    1,
    NULL
    );
}

//////////////////////////////////////////////
//    HELPER FUNCTIONS                      //
//////////////////////////////////////////////


/* 
 * Disables unused features to optimize power
 * Features disabled:
 *  1. USART0
 *  2. USART2
 *  3. USART3
 *  4. Timer5
 *  5. Timer4
 *  6. Timer3
 *  7. Timer1
 *  8. SPI
 */
void disable_unused_features() {
  int i;
  //Disable unused peripherals
  power_usart0_disable();
  power_usart2_disable();
  power_usart3_disable();

  power_timer5_disable();
  power_timer4_disable();
  power_timer3_disable();
  power_timer1_disable();

  power_spi_disable();

  //Change all unused pins to OUTPUT LOW
  for (i = 0; i <= 53; i++) {
    if (i != FLEXPIN && i != 20 && i != 21) {
      pinMode(i, OUTPUT);
      digitalWrite(i, LOW);
    } 
  }

  //Set all analog pins to OUTPUT LOW
  pinMode(A2, OUTPUT);
  pinMode(A3, OUTPUT);
  pinMode(A4, OUTPUT);
  pinMode(A5, OUTPUT);
  pinMode(A6, OUTPUT);
  pinMode(A7, OUTPUT);
  pinMode(A8, OUTPUT);
  pinMode(A9, OUTPUT);
  pinMode(A10, OUTPUT);
  pinMode(A11, OUTPUT);
  pinMode(A12, OUTPUT);
  pinMode(A13, OUTPUT);
  pinMode(A14, OUTPUT);
  pinMode(A15, OUTPUT);

  digitalWrite(A2, LOW);
  digitalWrite(A3, LOW);
  digitalWrite(A4, LOW);
  digitalWrite(A5, LOW);
  digitalWrite(A6, LOW);
  digitalWrite(A7, LOW);
  digitalWrite(A8, LOW);
  digitalWrite(A9, LOW);
  digitalWrite(A10, LOW);
  digitalWrite(A11, LOW);
  digitalWrite(A12, LOW);
  digitalWrite(A13, LOW);
  digitalWrite(A14, LOW);
  digitalWrite(A15, LOW);
}

/*
 * Select which channel to read the data from
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
  unsigned long start_time = 0;
  unsigned long current_time = 0;
  Serial1.write(SYNC);

  start_time = millis();
  while (received_byte != ACK) {
    // Wait until response received from RPi
    while(!Serial1.available()) {
      current_time = millis();
      if (current_time - start_time >= 2000) {
        Serial1.write(SYNC);
        start_time = millis();       
      }
    };
    // -48 since serial monitor/pi sends ascii characters
    received_byte = Serial1.read();
  }
  Serial1.write(SYNC_ACK);
  connection_established = true;

  //Flush buffer
   if ( xSemaphoreTake( xMsgBuffSemaphore, ( TickType_t ) 5 ) == pdTRUE ) { 
     msg_buffer.strt = 0;
     msg_buffer.bck = 0;
     msg_buffer.buff_size_remaining = RAW_BUFF_SIZE;
     xSemaphoreGive( xMsgBuffSemaphore );
   }
}

/* 
* Transfer data to RPi
*/
void transmit_data_from_buffer() {

  uint8_t received_byte = NONE;
  unsigned long start_time = 0;
  unsigned long current_time = 0;
  // Transmit data
  if (msg_buffer.buff_size_remaining < RAW_BUFF_SIZE) {
    if ( xSemaphoreTake( xMsgBuffSemaphore, ( TickType_t ) 5 ) == pdTRUE ) {
      uint8_t *current_msg_ptr =  msg_buffer.data_buffer[msg_buffer.strt];
      while (received_byte != CHK) {
        //Transmit data
        Serial1.write(current_msg_ptr, MSG_LEN);
        // Wait for response from RPi
        start_time = millis();
        while(!Serial1.available()) {
          current_time = millis();
          if (current_time - start_time >= 2000) {
            connection_established = false;
            received_byte = NONE;
            xSemaphoreGive( xMsgBuffSemaphore );
            return;
          }
        };
        received_byte = Serial1.read();
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
      sensorValueA0 = (sensorValueA0 / (float)NUM_SAMPLES * 5.1) / 1024.0;
      voltageOut = (sensorValueA1 / (float)NUM_SAMPLES * 5.08) / 1024.0;

      // Calculate Vin from Vout and two resistor
      // Battery V = 5.224, Voltage across resistor = 2.608
      // division factor = 2.001533742331288343558282208589
      voltageIn = voltageOut * 2;

      // Current value
      // Following the equation given by the INA169 datasheet to
      // determine the current flowing through RS. Assume RL = 10k
      // Is = (Vout x 1k) / (RS x RL)
      current = (sensorValueA0 / (RS * 10.0));
      
      // Power value
      power = current * voltageIn;

      
      // Energy value
      if (power != 0) {
        currTime = millis();
        elapsedTime = (currTime - prevTime) / 3600000.0;
        prevTime = currTime;
        energy = energy + (power * elapsedTime);
      }

      power_data[0] = voltageIn * 100;
      power_data[1] = current * 100;
      power_data[2] = power * 100;
      power_data[3] = energy * 1000;


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
    long start_time = millis();
    if (!connection_established) {
      establish_connection();
      //transmit_data_from_buffer();
    } else {
      transmit_data_from_buffer();
    }
    //Sleep until next scheduled time
    vTaskDelayUntil(&xLastWakeTime, xDelay);
  }
}

void TaskReadData(void *pvParameters) {
  const TickType_t xDelay = READ_DATA_DELAY / portTICK_PERIOD_MS;
  TickType_t xLastWakeTime;
  xLastWakeTime = xTaskGetTickCount();
  for(;;) {
    long start_time = millis();
    update_power_readings();
    if ( xSemaphoreTake( xMsgBuffSemaphore, ( TickType_t ) 5 ) == pdTRUE ) {  
      uint8_t *current_msg_ptr =  msg_buffer.data_buffer[msg_buffer.bck];
      uint8_t checksum = 0;
      int16_t msg_buffer_index = 0;
      // 0 - Main board, 6- left, 7 - right
      for (int i = 0; i < MPU_COUNT; i++) {
        if (i == 1 ) {
          tcaselect(6);
        } else if (i == 2) {
          tcaselect(7);
        } else {
          tcaselect(i);
        }
        Wire.beginTransmission(MPU);
        Wire.write(0x3B);  
        Wire.endTransmission(false);
        Wire.requestFrom(MPU,14,true);  

        /* SENSOR IDs
         * j = 0 - 2 : AcX,Y,Z
         * j = 3     : Tmp
         * j = 4 - 6 : GyX,Y,Z
         */
          for (int j = 0; j < SENSOR_PER_MPU; j++) {
            int16_t data = Wire.read()<<8|Wire.read();
            if (j != 3) {
              if (j <= 2) {
                data = data / 6144;
              } else {
                data = data / 131;
              }
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
      int16_t Flex = digitalRead(FLEXPIN);
      uint8_t lsb = (Flex & 0x00FF);
      uint8_t msb = (Flex & 0xFF00) >> 8;
      checksum ^= lsb;
      current_msg_ptr[msg_buffer_index++] = lsb;
      checksum ^= msb;
      current_msg_ptr[msg_buffer_index++] = msb;

      //Get power readings
      for(int k = 0; k < 4; k++) {
        int16_t data = power_data[k];
        uint8_t lsb = (data & 0x00FF);
        uint8_t msb = (data & 0xFF00) >> 8;
        checksum ^= lsb;
        current_msg_ptr[msg_buffer_index++] = lsb;
        checksum ^= msb;
        current_msg_ptr[msg_buffer_index++] = msb;
      }

      current_msg_ptr[msg_buffer_index] = checksum;
      //update buffer state and allow current data to be overwritten
      if (msg_buffer.buff_size_remaining > 0) {
        msg_buffer.buff_size_remaining--;
      }
      msg_buffer.bck++;
      if (msg_buffer.bck >= RAW_BUFF_SIZE) {
        msg_buffer.bck = 0;
      }
      xSemaphoreGive( xMsgBuffSemaphore );
    }

    vTaskDelayUntil(&xLastWakeTime, xDelay);
  }
}

void loop() {
  // put your main code here, to run repeatedly:

}
