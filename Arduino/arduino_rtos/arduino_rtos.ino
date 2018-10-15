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

#define TCAADDR 0x70
#define FLEXPIN 11

void TaskSendMessage(void *pvParameters);
void TaskFormatMessage(void * pvParameters);
void TaskReadData(void *pvParameters);

void establish_connection();
void transmit_data_from_buffer();
void terminate_connection();

void send_16bit(uint16_t data);
void tcaselect(uint8_t i);

cbuffer_t msg_buffer;

SemaphoreHandle_t xMsgBuffSemaphore;

const int MPU=0x68; 

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

          /*
           * j = 0 : AcX
           * j = 1 : AcY
           * j = 2 : AcZ
           * j = 3 : Tmp
           * j = 4 : GyX
           * j = 5 : GyY
           * j = 6 : GyZ
           */
            for (int j = 0; j < SENSOR_PER_MPU; j++) {
              int16_t data = j + 1;
              //int16_t data = Wire.read()<<8|Wire.read();
              if (j != 3) {
                uint8_t lsb = (data & 0x00FF);
                uint8_t msb = (data & 0xFF00) >> 8;
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
