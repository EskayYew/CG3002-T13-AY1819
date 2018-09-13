//File containing description of the circular buffers
#include "config.h"

typedef struct circular_buffer {
  int buff_size_remaining = RAW_BUFF_SIZE;
  int strt = 0;
  int bck = 0;
  uint8_t data_buffer[RAW_BUFF_SIZE][SENSOR_COUNT];
} cbuffer_t;

