//Contains constants used in Arduino to Pi communications

#define SENSOR_COUNT 1

//Packet types
#define SYNC     (uint8_t)0
#define ACK      (uint8_t)1
#define SYNC_ACK (uint8_t)2
#define ID       (uint8_t)3
#define DATA     (uint8_t)4
#define CHK      (uint8_t)5
#define NACK     (uint8_t)6
#define FIN      (uint8_t)7
#define NONE     (uint8_t)8

typedef struct {
  uint8_t checksum = 0;
  uint8_t reading_list[SENSOR_COUNT];
} DataPacket_t;

