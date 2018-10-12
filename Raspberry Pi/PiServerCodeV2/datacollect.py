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
        self.msg_len = SENSOR_COUNT
        
        self.buffer = bufferX
        # Setup serial port
        self.ser = serial.Serial('/dev/ttyS0', 115200)
        self.ser.reset_input_buffer()
        self.ser.reset_output_buffer()
        
        self.data_buff = []
        self.chksum = 0
        self.is_id = True

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
    # read data sequentially and store into self.data_buff
    # do checksum and compare with checksum that is on the last position of data_buff 
        while (len(self.data_buff) < self.msg_len):
            lowByte = self.ser.read()
            highByte = self.ser.read()
            data = (highByte << 8) | lowByte

            # data = self.ser.read()
            # print(data)
            self.chksum ^= data
            self.data_buff.append(data)

        # print(chksum)

        print(self.data_buff)
        
        # if checksum matches, then data is clean and ready to be stored into circular buffer
        if (self.data_buff[self.msg_len - 1] == self.chksum):
            
            # print("Data received and verified")
            # must lock when feeding data to buffer. 
            processLock.acquire()
            self.buffer.append(self.data_buff)
            print(self.buffer.getSize)
            processLock.release()
            
            self.ser.write(b'1')
        else:
            self.ser.write(b'6')
            print("Checksum error")

        # Wait for FIN packet
        while(self.ser.read() != b'\x07'):
            pass
        self.ser.write(b'7')
        while(self.ser.read() != b'\x01'):
            pass

        self.data_buff = []
        self.chksum = 0

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
            SENSOR_COUNT = 26

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