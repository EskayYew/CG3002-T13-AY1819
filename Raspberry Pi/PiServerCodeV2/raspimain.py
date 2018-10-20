import threading
import time
import serial
import socket
import sys
import base64
from Crypto import Random
from Crypto.Cipher import AES
from CircleBuffer import CircleBuffer

# Applying threading on different processes between classes
# Credits to https://stackoverflow.com/questions/17774768/python-creating-a-shared-variable-between-threads
# Absolutely necessary if you are doing different processes

processLock = threading.Lock()

class MachineLearning(threading.Thread):
    def __init__(self, bufferX, client):
        threading.Thread.__init__(self)
        self.databuffer = []
        self.buffer = bufferX
        self.sender = client
        self.actionSent = False

    def processData(self, bufferY):
        #print('Machine Learning')
        return 'chicken'

    def processAction(self):
        self.databuffer = self.buffer.get()

        # machine learning will iterate through databuffer and determine action
        if(self.buffer.getSize >= 100):
            action = self.processData(self.databuffer)

        # process lock required so as to prevent any corruption of any the sent data to server.
        processLock.acquire()
        print(action)
        if action != 'idle':
            self.sender.sendMessage(action)
            self.actionSent = True
        processLock.release()

        if self.actionSent is True:
            self.buffer.reset()
            self.databuffer = []
            self.actionSent = False
        
        threading.Timer(2, self.processAction).start()

    # suppose to start after 60 seconds. 5 is dummy value for testing.
    def run(self):
        threading.Timer(5, self.processAction).start()

class Receiver(threading.Thread):
    def __init__(self, bufferX, dataList):
        threading.Thread.__init__(self)

        self.SENSOR_COUNT = 23
        
        self.energy = 0.000
        self.buffer = bufferX
        self.connection_established = False

        self.dataList = dataList
        # Setup serial port
        self.ser = serial.Serial(            
            #port = 'COM5',
            port='/dev/ttyS0',
            baudrate = 115200,
            parity=serial.PARITY_NONE,
            stopbits=serial.STOPBITS_ONE,
            bytesize=serial.EIGHTBITS,
            #timeout=0.1
        )
        self.ser.flushInput()
        self.ser.flushOutput()

        self.ser.reset_input_buffer()
        self.ser.reset_output_buffer()
        
        self.data_buff = []
        self.byteArray = []

    def checkByteArray(self, bArray):
        newArray = []
        checksum = 0

        chkPos = self.SENSOR_COUNT

        # go from 0 to 22 since sensorcount is 23(46)
        for counter in range (0, chkPos):
            byte1 = bArray[counter * 2]
            checksum = checksum ^ (int.from_bytes(byte1, byteorder="big", signed=True))
            byte2 = bArray[counter * 2 + 1]
            checksum = checksum ^ (int.from_bytes(byte2, byteorder="big", signed=True))
            combinedValue = int.from_bytes(byte2 + byte1, byteorder="big", signed=True)
            
            if counter >= 19 and counter <= 21:
                combinedValue /= 100
            if counter == 22:
                combinedValue /= 1000
            
            newArray.append(combinedValue)

        self.energy += newArray[22]

        newArray[22] = self.energy
        self.dataList = newArray[19:22]

        chkPos = chkPos*2

        arrayChecksum = (int.from_bytes(bArray[chkPos] , byteorder="big", signed=True))
        # checksum is at 46th position of bArray
        # if checksum matches, then data is clean and ready to be stored into circular buffer
        if (checksum == arrayChecksum):            
            self.ser.write(b'C')
            return newArray
        else:
            self.ser.write(b'N')
            
            print("Checksum error")
            print(bArray)
            print(newArray)
            print(checksum)
            print(arrayChecksum)
            
            return None
    
    def establish_connection(self):
        # Wait for SYNC packet
        while(self.ser.read() != b'S'):
            pass
        self.ser.write(b'A')
        # Wait for SYNC-ACK packet
        while(self.ser.read() != b'H'):
            pass

        self.connection_established = True
        print("Connection Established")
    
    def read_data(self):
        #will be receiving 47 array bytes, 0 to 46
        while (len(self.byteArray) < 47):
            startTime = time.time()
            while(self.ser.in_waiting == 0):
                currentTime = time.time()
                if (currentTime - startTime >= 2.0):
                    self.byteArray = []
                    self.data_buff = []
                    self.connection_established = False
                    print('termination')
                    return
                
            rcv = self.ser.read()
            self.byteArray.append(rcv)
                            
        self.data_buff = self.checkByteArray(self.byteArray)
        
        if(self.data_buff is not None):
            processLock.acquire()
            self.buffer.append(self.data_buff)
            processLock.release()
            
        if(self.buffer.getSize() % 25 == 0):
            print(self.buffer.getSize())

        self.byteArray = []
        self.data_buff = []
           
    def communicate(self):
        if not self.connection_established:
            self.establish_connection()
            #self.read_data()
        else:
            self.read_data()

    def receiveLoop(self):
        # newTime = time.time() + 5
        self.communicate()
        # threading.Timer(newTime - time.time(), self.printSelf).start()
        threading.Timer(0.03, self.receiveLoop).start()

    def run(self):
        self.receiveLoop()

class Communication:

    def __init__(self, host, port, dataList):
        self.host = host
        self.port = int(port)
        self.bs = 16
        self.key = bytes("1234123412341234".encode("utf8"))
        self.dataList = dataList

        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client.connect((self.host, self.port))
        print("[+] You are currently connected to ", self.host + ":" + str(self.port))

        self.actions = {'wipers':'wipers', 'number7':'number7', 'chicken':'chicken',
            'sidestep':'sidestep', 'turnclap':'turnclap', 'logout':'logout'}

    def encrypt(self, message):
        text = self._pad(message)
        iv = Random.new().read(AES.block_size)
        cipher = AES.new(self.key, AES.MODE_CBC, iv)
        return base64.b64encode(iv + cipher.encrypt(text))

    def _pad(self, s):
        return bytes(s + (self.bs - len(s) % self.bs) * chr(self.bs - len(s) % self.bs), 'utf-8')

    def format(self, message):
        return '#{}|{0:.2f}|{0:.2f}|{0:.2f}|{0:.2f}|'.format(self.actions[message], self.dataList[0], self.dataList[1], self.dataList[2], self.dataList[3])

    def sendMessage(self, message):
        message = self.format(message)
        message = self.encrypt(message)
        self.client.send(message)    

class Pi:
    def __init__(self, host, port):
        self.dataList = [4.65, 2.00, 1.98, 10.00]
        self.threads = []
        self.buffer = CircleBuffer(250)
        self.client = Communication(host, port, self.dataList)

    def main(self):
        receiver = Receiver(self.buffer, self.dataList)
        machine = MachineLearning(self.buffer, self.client)

        self.threads.append(machine)
        self.threads.append(receiver)

        for t in self.threads:
            t.daemon = True
            t.start()

        while True:
            time.sleep(0.001)

        print('Program End')

if __name__ == '__main__':
    host = sys.argv[1]
    port = sys.argv[2]
    pi = Pi(host, port)
    pi.main()