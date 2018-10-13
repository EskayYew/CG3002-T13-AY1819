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
    def __init__(self, bufferX):
        threading.Thread.__init__(self)
        
        self.SENSOR_COUNT = 26
        self.msg_len = self.SENSOR_COUNT * 2
        
        self.buffer = bufferX
        # Setup serial port
        self.ser = serial.Serial(            
            port='/dev/ttyS0',
            baudrate = 115200,
            parity=serial.PARITY_NONE,
            stopbits=serial.STOPBITS_ONE,
            bytesize=serial.EIGHTBITS,
            timeout=0.1
        )

        self.ser.reset_input_buffer()
        self.ser.reset_output_buffer()
        
        self.data_buff = []
        self.byteArray = []
        
    def checkByteArray(self, bArray):
        newArray = []
        checksum = 0

        chkPos = self.SENSOR_COUNT-1

        # go from 0 to 24 since sensorcount is 25(50,51)
        for counter in range (0, chkPos):
            byte1 = bArray[counter * 2]
            checksum = checksum ^ (int.from_bytes(byte1, byteorder="big", signed=True))
            byte2 = bArray[counter * 2 + 1]
            checksum = checksum ^ (int.from_bytes(byte2, byteorder="big", signed=True))
            combinedValue = int.from_bytes(byte1 + byte2, byteorder="big", signed=True)
            
            newArray.append(combinedValue)

        chkPos = chkPos*2

        # checksum is at 50 to 51 position of bArray
        # if checksum matches, then data is clean and ready to be stored into circular buffer
        if (checksum == (int.from_bytes(bArray[chkPos] + bArray[chkPos+1] , byteorder="big", signed=True))):            
            self.ser.write(b'1')
            return newArray
        else:
            self.ser.write(b'6')
            print("Checksum error")
            return None

    def communicate(self):

        # Wait for SYNC packet
        while(self.ser.read() != b'\x00'):
            pass
        #print("connection with arduino established")
        self.ser.write(b'1')
        # Wait for SYNC-ACK packet
        while(self.ser.read() != b'\x02'):
            pass

        # handshake established with handshake flag

        #will be receiving 52 array bytes, 0 to 51
        while (len(self.data_buff) < self.msg_len):
            rcv = self.ser.read()
            if (rcv != b'\r' and rcv != b'\n'):
                self.byteArray.append(rcv)

        self.data_buff = self.checkByteArray(self.byteArray)
        
        if(self.data_buff is not None):
            processLock.acquire()
            self.buffer.append(self.data_buff)
            processLock.release()

        print(self.data_buff)

        # Wait for FIN packet
        while(self.ser.read() != b'\x07'):
            pass
        self.ser.write(b'7')
        while(self.ser.read() != b'\x01'):
            pass

        self.byteArray.clear()
        self.data_buff.clear()
        self.chksum = 0

    def receiveLoop(self):
        # newTime = time.time() + 5
        self.communicate()
        # threading.Timer(newTime - time.time(), self.printSelf).start()
        threading.Timer(0.1, self.receiveLoop).start()

    def run(self):
        self.receiveLoop()

class Pi:
    def __init__(self):
        self.dataList = [0, 0, 0, 0]
        self.threads = []
        self.buffer = CircleBuffer(250)

    def main(self):
        try:
            receiver = Receiver(self.buffer)
            
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