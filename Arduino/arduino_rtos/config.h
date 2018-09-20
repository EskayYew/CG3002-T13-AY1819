// Configuration file containing all the global constants

// Currently assume that configTICK_RATE_HZ is 1000 hz, delay is in ticks

// System variables
#define STACK_SIZE       200
#define SENSOR_COUNT     5
#define USB_DEBUG_MODE   1

//buffer sizes
#define RAW_BUFF_SIZE    100
#define MSG_LEN          (2 * SENSOR_COUNT) + 1 

// Task delays
#define READ_DATA_DELAY  50
#define SEND_DELAY       50




