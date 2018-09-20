//File containing main entry point

#include <Arduino_FreeRTOS.h>
#include <semphr.h>

#include "comms_protocol.h"
#include "config.h"
#include "data_buffers.h"

void TaskSendMessage(void *pvParameters);
void TaskFormatMessage(void * pvParameters);
void TaskReadData(void *pvParameters);

void establish_connection();
void transmit_data_from_buffer();
void terminate_connection();

cbuffer_t msg_buffer;

SemaphoreHandle_t xMsgBuffSemaphore;

void setup() {
  // Initialize serial communication - 115200 bps,8 Data, 1 Stop, 0 Parity
  // Temporarily using Serial for debugging, will move over to Serial1
  if (USB_DEBUG_MODE) {
    Serial.begin(115200, SERIAL_8N1);
  }
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
* Initiate communication with RPi 
*/
void establish_connection() {
  uint8_t received_byte = NONE;
  uint16_t resend_timer = 0;
  Serial1.write(SYNC);
  if (USB_DEBUG_MODE) {
    Serial.println(SYNC);
  }
  while (received_byte != ACK) {
    // Wait until response received from RPi
    // TODO - add time out
    while(!Serial1.available()) {
      if (resend_timer == 1000) {
        Serial1.write(SYNC); 
        resend_timer = 0;       
      } else {
        resend_timer++;
      }
    }
    // -48 since serial monitor/pi sends ascii characters
    received_byte = Serial1.read() - 48;
    if (USB_DEBUG_MODE) {
      Serial.println(received_byte);
    }
  }
  Serial1.write(SYNC_ACK);
  if (USB_DEBUG_MODE) {
    Serial.println(SYNC_ACK);
  } 
}

/* 
* Start data transfer
*/
void transmit_data_from_buffer() {

  uint8_t received_byte = NONE;
  while (received_byte != ACK) {
    // Transmit data
    if ( xSemaphoreTake( xMsgBuffSemaphore, ( TickType_t ) 5 ) == pdTRUE ) {
      uint8_t *current_msg_ptr =  msg_buffer.data_buffer[msg_buffer.strt];
      for(int i = 0; i < MSG_LEN; i++ ) {
        Serial1.write(current_msg_ptr[i]);
        if (USB_DEBUG_MODE){
          Serial.println(current_msg_ptr[i]);
        } 
      }
      //update buffer state and allow current data to be overwritten
      msg_buffer.buff_size_remaining++;
      msg_buffer.strt++;
      if (msg_buffer.strt >= RAW_BUFF_SIZE) {
           msg_buffer.strt = 0;
      }
      xSemaphoreGive( xMsgBuffSemaphore );
    }
    // Wait for reponse from RPi
    while(!Serial1.available()) {};
    received_byte = Serial1.read() - 48;
  }
}

/* 
* Terminate communication with RPi
*/
void terminate_connection(){
  uint8_t received_byte = NONE;
  Serial1.write(FIN);
  if (USB_DEBUG_MODE) {
    Serial.println(FIN);
  }
  while (received_byte != FIN) {
    // Wait until response received from RPi
    // TODO - add time out
    while(!Serial1.available()) {};
    received_byte = Serial1.read() - 48;
  }
  Serial1.write(ACK);
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
        int msg_buffer_index = 0;
        for (int i = 0; i < SENSOR_COUNT; i++) {
          // Sensor ID
          current_msg_ptr[msg_buffer_index++] = i;
          // Sensor Data
          current_msg_ptr[msg_buffer_index++] = i + 1;
          checksum ^= i + 1;
        }
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
