// Configuration file containing all the global constants

// Currently assume that configTICK_RATE_HZ is 1000 hz, delay is in ticks

// System variables
#define STACK_SIZE       200
#define SENSOR_PER_MPU   7
#define MPU_COUNT        4
#define POWER_DATA_COUNT 4
#define USB_DEBUG_MODE   0

//buffer sizes
#define RAW_BUFF_SIZE    100
// + 1 for flex sensor and + 1 for checksum
#define MSG_LEN          2 * (POWER_DATA_COUNT + (MPU_COUNT * (SENSOR_PER_MPU - 1)) + 1) + 1  

// Task delays
#define READ_DATA_DELAY  200
#define SEND_DELAY       500




