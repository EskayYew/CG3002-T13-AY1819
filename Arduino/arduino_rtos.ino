#include <Arduino_FreeRTOS.h>
#include <semphr.h>
#include "comms_protocol.h"


//Currently assume that configTICK_RATE_HZ is 1000 hz, delay is in ticks
#define SEND_DELAY     5000
#define STACK_SIZE     200

#define RAW_BUFF_SIZE  100
#define MSG_LEN        (2 * SENSOR_COUNT) + 1
#define USB_DEBUG_MODE 1 

void TaskSendMessage(void *pvParameters);
void TaskFormatMessage(void * pvParameters);
void TaskReadData(void *pvParameters);

uint8_t msg_buffer[MSG_LEN];

SemaphoreHandle_t xRawBuffSemaphore;
SemaphoreHandle_t xMsgBuffSemaphore;

void setup() {
  // Initialize serial communication - 115200 bps,8 Data, 1 Stop, 0 Parity
  // Temporarily using Serial for debugging, will move over to Serial1
  Serial.begin(115200, SERIAL_8N1);

  for (int i = 0; i < MSG_LEN; i++) {
    msg_buffer[i] = i + 1;
  }

  xTaskCreate(
    TaskSendMessage,
    (const portCHAR *) "SendMessage",
    STACK_SIZE,
    NULL,
    1,
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
    Serial.write(SYNC_ACK);
    Serial.println(SYNC_ACK);
    
  /* 
   * Start data transfer
  */
    received_byte = NONE;
    while (received_byte != ACK) {
      // Transmit data
      for(int i = 0; i < MSG_LEN; i++ ) {
        //Serial.write(msg_buffer[i]);
        Serial.println(msg_buffer[i]); 
      }
      // Wait for reponse from RPi
      while(!Serial.available()) {};
      received_byte = Serial.read() - (48 * USB_DEBUG_MODE);
    }

  /* 
   * Terminate communication with RPi
  */
    Serial.write(FIN);
    Serial.println(FIN);
    while (received_byte != FIN) {
      // Wait until response received from RPi
      // TODO - add time out
      while(!Serial.available()) {};
      received_byte = Serial.read() - (48 * USB_DEBUG_MODE);
    }
    Serial.write(ACK);
    Serial.println(ACK);
    received_byte = NONE;

    //Sleep until next scheduled time
    vTaskDelayUntil(&xLastWakeTime, xDelay);
  }
  
}

void loop() {
  // put your main code here, to run repeatedly:

}
