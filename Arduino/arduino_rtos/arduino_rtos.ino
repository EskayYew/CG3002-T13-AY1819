//File containing main entry point

#include <Arduino_FreeRTOS.h>
#include <semphr.h>

#include "comms_protocol.h"
#include "config.h"
#include "data_buffers.h"

void TaskSendMessage(void *pvParameters);
void TaskFormatMessage(void * pvParameters);
void TaskReadData(void *pvParameters);

uint8_t msg_buffer[MSG_LEN];
cbuffer_t raw_data_buffer;

SemaphoreHandle_t xRawBuffSemaphore;
SemaphoreHandle_t xMsgBuffSemaphore;

void setup() {
  // Initialize serial communication - 115200 bps,8 Data, 1 Stop, 0 Parity
  // Temporarily using Serial for debugging, will move over to Serial1
  Serial.begin(115200, SERIAL_8N1);

  /*
   * Initialize semaphores
   */
  if ( xRawBuffSemaphore == NULL ) {
    xRawBuffSemaphore = xSemaphoreCreateMutex(); 
    if ( ( xRawBuffSemaphore ) != NULL ) {
      xSemaphoreGive( ( xRawBuffSemaphore ) );
    }
  } 

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
    TaskFormatMessage,
    (const portCHAR *) "FormatMessage",
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
    3,
    NULL
    );
}

void TaskSendMessage(void *pvParameters) {
  const TickType_t xDelay = SEND_DELAY / portTICK_PERIOD_MS;
  TickType_t xLastWakeTime;
  xLastWakeTime = xTaskGetTickCount();
  uint8_t received_byte = NONE;
  
  for(;;) {
  /* 
   * Initiate communication with RPi 
  */
    Serial.write(SYNC);
    Serial.println(SYNC);
    while (received_byte != ACK) {
      // Wait until response received from RPi
      // TODO - add time out
      while(!Serial.available()) {};
      // -48 for usb-debug mode since serial monitor sends ascii characters
      received_byte = Serial.read() - (48 * USB_DEBUG_MODE);
      Serial.println(received_byte);
    }
    //Serial.write(SYNC_ACK);
    Serial.println(SYNC_ACK);
    
  /* 
   * Start data transfer
  */
    received_byte = NONE;
    while (received_byte != ACK) {
      // Transmit data
      if ( xSemaphoreTake( xMsgBuffSemaphore, ( TickType_t ) 5 ) == pdTRUE ) {
        for(int i = 0; i < MSG_LEN; i++ ) {
          //Serial.write(msg_buffer[i]);
          Serial.println(msg_buffer[i]); 
        }
        xSemaphoreGive( xMsgBuffSemaphore );
      }
      // Wait for reponse from RPi
      while(!Serial.available()) {};
      received_byte = Serial.read() - (48 * USB_DEBUG_MODE);
    }

  /* 
   * Terminate communication with RPi
  */
    //Serial.write(FIN);
    Serial.println(FIN);
    while (received_byte != FIN) {
      // Wait until response received from RPi
      // TODO - add time out
      while(!Serial.available()) {};
      received_byte = Serial.read() - (48 * USB_DEBUG_MODE);
    }
    //Serial.write(ACK);
    Serial.println(ACK);
    received_byte = NONE;

    //Sleep until next scheduled time
    vTaskDelayUntil(&xLastWakeTime, xDelay);
  }
  
}

void TaskFormatMessage(void * pvParameters){
  const TickType_t xDelay = MSG_FORMAT_DELAY / portTICK_PERIOD_MS;
  TickType_t xLastWakeTime;
  xLastWakeTime = xTaskGetTickCount();

  for(;;) {
    //Sleep until next scheduled time
    if ( xSemaphoreTake( xRawBuffSemaphore, ( TickType_t ) 5 ) == pdTRUE ) {
      if ( xSemaphoreTake( xMsgBuffSemaphore, ( TickType_t ) 5 ) == pdTRUE ) {
        if (raw_data_buffer.buff_size_remaining != RAW_BUFF_SIZE) {
          uint8_t checksum = 0;
          uint8_t *current_data_ptr =  raw_data_buffer.data_buffer[raw_data_buffer.strt];
          for (int i = 0; i < MSG_LEN - 1; i += 2) {
            msg_buffer[i] = i;
            checksum ^= current_data_ptr[i];
            msg_buffer[i + 1] = current_data_ptr[i]; 
          }
          msg_buffer[MSG_LEN - 1] = checksum;
  
          //update buffer state and allow current data to be overwritten
          raw_data_buffer.buff_size_remaining++;
          raw_data_buffer.strt++;
          if (raw_data_buffer.strt >= RAW_BUFF_SIZE) {
            raw_data_buffer.strt = 0;
          }
        }     
        xSemaphoreGive( xMsgBuffSemaphore );
      }
      xSemaphoreGive( xRawBuffSemaphore );
    }
    vTaskDelayUntil(&xLastWakeTime, xDelay);
  }
}

void TaskReadData(void *pvParameters) {
  const TickType_t xDelay = READ_DATA_DELAY / portTICK_PERIOD_MS;
  TickType_t xLastWakeTime;
  xLastWakeTime = xTaskGetTickCount();
  bool flag = true;
  for(;;) {
    if ( xSemaphoreTake( xRawBuffSemaphore, ( TickType_t ) 5 ) == pdTRUE ) {
      if (raw_data_buffer.buff_size_remaining > 0) {
        uint8_t *current_data_ptr =  raw_data_buffer.data_buffer[raw_data_buffer.bck];
        for (int i = 0; i < SENSOR_COUNT; i++) {
          if (flag) {
            current_data_ptr[i] = i;
          } else {
            current_data_ptr[i] = SENSOR_COUNT;
          }
        }
        //update buffer state and allow current data to be overwritten
        raw_data_buffer.buff_size_remaining--;
        raw_data_buffer.bck++;
        if (raw_data_buffer.bck >= RAW_BUFF_SIZE) {
          raw_data_buffer.bck = 0;
        }
      }
      flag = !flag;
      xSemaphoreGive( xRawBuffSemaphore );
    }
    vTaskDelayUntil(&xLastWakeTime, xDelay);
  }
}

void loop() {
  // put your main code here, to run repeatedly:

}
