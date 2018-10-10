import threading
import time
import serial
import csv
import sys
from CircleBuffer import CircleBuffer

# Applying threading on different processes between classes
# Credits to https://stackoverflow.com/questions/17774768/python-creating-a-shared-variable-between-threads
# Absolutely necessary if you are doing different processes

processLock = threading.Lock()

class MachineLearning(threading.Thread):
    def __init__(self, bufferX):
        threading.Thread.__init__(self)
        self.databuffer = []
        self.buffer = bufferX
   
    def processData(self, bufferY):
        print('Machine Learning')

        return 'chicken'

    def processAction(self):
        self.databuffer = self.buffer.get()

        # machine learning will iterate through databuffer and determine action
        # if(self.buffer.getSize == 250):
        action = self.processData(self.databuffer)

        processLock.acquire()
        print(action)
        processLock.release()

        # self.buffer.reset()
        # self.databuffer = []        
        
        threading.Timer(2, self.processAction).start()

    def run(self):
        threading.Timer(5, self.processAction).start()

class Receiver(threading.Thread):
    def __init__(self, SENSOR_COUNT, bufferX):
        threading.Thread.__init__(self)
        self.SENSOR_COUNT = SENSOR_COUNT
        self.msg_len = (2 * self.SENSOR_COUNT) + 1 
        
        self.buffer = bufferX
        # Setup serial port
        self.ser = serial.Serial('/dev/ttyS0', 115200)
        self.ser.reset_input_buffer()
        self.ser.reset_output_buffer()
        
        self.data_buff = []
        self.chksum = b'0'
        self.is_id = True
        self.messages_recieved = 0

    def handshake(self):
        # Wait for SYNC packet
        while(self.ser.read() != b'\x00'):
            pass
        #print("connection with arduino established")
        self.ser.write(b'1')
        # Wait for SYNC-ACK packet
        while(self.ser.read() != b'\x02'):
            pass

        #print("handshake with arduino established")
    
        
    def communicate(self):
    #while True:
        while (len(self.data_buff) < self.msg_len):
            data = self.ser.read()
            #print(data)
            if (data != b'\r' and data != b'\n'):
                #print(ord(data))
                if not self.is_id:
                    self.chksum = bytes(x ^ y for x, y in zip(self.chksum, data))
                self.data_buff.append(data)
                self.is_id = not self.is_id
        # print(chksum)
        # print(data_buff)
        if (str(ord((self.data_buff[self.msg_len - 1]))) == self.chksum.decode()):
            self.messages_recieved += 1
            #print("Data received and verified")
            print('{} messages received'.format(self.messages_recieved))
            self.ser.write(b'1')
        else:
            self.ser.write(b'6')
            print("Checksum error")
            print('expected: {} recv: {}'.format(str(ord((self.data_buff[self.msg_len - 1]))), self.chksum.decode()))
        # Wait for FIN packet
        while(self.ser.read() != b'\x07'):
            pass
        self.ser.write(b'7')
        while(self.ser.read() != b'\x01'):
            pass
        #print("Message received")
        #print(self.data_buff)
        processLock.acquire()
        self.buffer.append(self.data_buff)
        print(self.data_buff)
        print(self.buffer.getSize)
        processLock.release()
        self.data_buff = []
        self.is_id = True
        self.chksum = b'0'

    def receiveLoop(self):
        # newTime = time.time() + 5
        self.handshake()
        self.communicate()
        # threading.Timer(newTime - time.time(), self.printSelf).start()
        threading.Timer(0.05, self.receiveLoop).start()

    def run(self):
        self.receiveLoop()

class Pi:
    def __init__(self):
        self.dataList = [0, 0, 0, 0]
        self.threads = []
        self.buffer = CircleBuffer(250)

    def main(self):
        try:
            SENSOR_COUNT = 5

            receiver = Receiver(SENSOR_COUNT, self.buffer)
            
            machine = MachineLearning(self.buffer)

            self.threads.append(machine)
            self.threads.append(receiver)

            for t in self.threads:
                t.daemon = True
                t.start()

            while True:
                time.sleep(0.001)

        except KeyboardInterrupt:

            file = str(sys.argv[1])
            databuffer = self.buffer.get()
            myFile = open(file, 'w', newline='')
            with myFile:
                writer = csv.writer(myFile)
                for items in databuffer:
                    writer.writerow(items)
            myFile.close()
            print("Writing complete")
            print('Program End')
            sys.exit(1)

if __name__ == '__main__':
    pi = Pi()
    pi.main()