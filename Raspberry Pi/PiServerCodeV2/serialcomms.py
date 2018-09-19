import serial
#use https://github.com/eric-wieser/numpy_ringbuffer

class Receiver:

    def __init__(self, SENSOR_COUNT):
        self.SENSOR_COUNT = SENSOR_COUNT
        self.msg_len = (2 * self.SENSOR_COUNT) + 1 
        
        # Setup serial port
        self.ser = serial.Serial('COM5', 115200)
        self.data_buff = []
        self.chksum = b'0'
        self.is_id = True

    def handshake(self):
        # Wait for SYNC packet
        while(self.ser.read() != b'0'):
            pass
        print("connection with arduino established")
        self.ser.write(b'1')
        # Wait for SYNC-ACK packet
        while(self.ser.read() != b'2'):
            pass

        print("handshake with arduino established")
    
        
    def communicate(self):
        while True:
            while (len(self.data_buff) < self.msg_len):
                data = self.ser.read()
                if (data != b'\r' and data != b'\n'):
                    print(data.decode('utf-8'))
                    if not self.is_id:
                        self.chksum = bytes(x ^ y for x, y in zip(self.chksum, data))
                    self.data_buff.append(data)
                    self.is_id = not self.is_id
            # print(chksum)
            # print(data_buff)
            if ((self.data_buff[self.msg_len - 1]).decode() == str(ord(self.chksum))):
                print("Data received and verified")
                self.ser.write(b'1')
            else:
                self.ser.write(b'6')
                print("Checksum error")
                print('expected: {} recv: {}'.format(data, self.chksum))
            # Wait for FIN packet
            while(self.ser.read() != b'7'):
                pass
            self.ser.write(b'7')
            while(self.ser.read() != b'1'):
                pass
            print("Message received")
            print(self.data_buff)

def main():
    SENSOR_COUNT = 5

    receiver = Receiver(SENSOR_COUNT)
    receiver.handshake()
    receiver.communicate()

if __name__ == '__main__':
    main()
