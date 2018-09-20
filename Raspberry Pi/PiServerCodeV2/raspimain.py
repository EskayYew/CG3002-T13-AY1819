import threading
import time
import serial
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
        print(bufferY[0])
        return 'chicken'

    def processAction(self):
        self.databuffer = self.buffer.get()

        # machine learning will iterate through databuffer and determine action
        action = self.processData(self.databuffer)

        processLock.acquire()
        print(action)
        processLock.release()

        self.buffer.reset()
        self.databuffer = []
        threading.Timer(10, self.processAction).start()

    def run(self):
        threading.Timer(60, self.processAction).start()

class Receiver(threading.Thread):
    def __init__(self, SENSOR_COUNT):
        self.SENSOR_COUNT = SENSOR_COUNT
        self.msg_len = (2 * self.SENSOR_COUNT) + 1 
        
        # Setup serial port
        self.ser = serial.Serial('/dev/ttyS0', 115200)
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

    def printSelf(self):
        # newTime = time.time() + 5

        processLock.acquire()
        print('I am the Receiver')
        processLock.release()

        # threading.Timer(newTime - time.time(), self.printSelf).start()
        threading.Timer(0.05, self.printSelf).start()

    def run(self):
        self.printSelf()
        
class Pi:
    def __init__(self):
        self.dataList = [0, 0, 0, 0]
        self.threads = []
        self.buffer = CircleBuffer(50)

    def main(self):
        SENSOR_COUNT = 5

        receiver = Receiver(SENSOR_COUNT) 
        receiver.handshake()

        machine = MachineLearning(self.buffer)

        self.threads.append(machine)
        self.threads.append(receiver)

        for t in self.threads:
            t.daemon = True
            t.start()

        while True:
            time.sleep(0.001)

        print('Program End')

if __name__ == '__main__':
    pi = Pi()
    pi.main()