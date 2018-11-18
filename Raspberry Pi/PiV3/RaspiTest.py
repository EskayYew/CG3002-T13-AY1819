import threading
import time
import serial
import socket
import sys
import base64
from NeuralNet_Correlation_Model import DanceClassifierNN
from Crypto import Random
from Crypto.Cipher import AES
from RingBuffer import RingBuffer

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

        self.actions = {'WIPERS':'wipers', 'NUMBER7':'number7', 'CHICKEN':'chicken',
            'SIDESTEP':'sidestep', 'TURNCLAP':'turnclap', 'COWBOY':'cowboy',
            'SWING':'swing', 'MERMAID':'mermaid', 'SALUTE':'salute',
            'NUMBER6':'numbersix', 'LOGOUT':'logout'}

    def encrypt(self, message):
        text = self._pad(message)
        iv = Random.new().read(AES.block_size)
        cipher = AES.new(self.key, AES.MODE_CBC, iv)
        return base64.b64encode(iv + cipher.encrypt(text))

    def updateData(self, arrayData):
        self.dataList = arrayData

    def _pad(self, s):
        return bytes(s + (self.bs - len(s) % self.bs) * chr(self.bs - len(s) % self.bs), 'utf-8')

    def format(self, message):
        return '#{0}|{1:.2f}|{2:.2f}|{3:.2f}|{4:.2f}|'.format(self.actions[message], self.dataList[0], self.dataList[1], self.dataList[2], self.dataList[3])

    def sendMessage(self, message):
        message = self.format(message)
        message = self.encrypt(message)
        self.client.send(message)    

class Pi:
    def __init__(self, host, port):
        self.WINDOWSIZE = 100
        self.dataList = [4.65, 2.00, 1.98, 10.00]
        self.buffer = RingBuffer(self.WINDOWSIZE)
        self.client = Communication(host, port, self.dataList)
        self.movesSent = 0

        # Machine Learning
        self.model = DanceClassifierNN()
        self.executionTime = 0.0
        self.FlushTime = 2.0
        self.flushFlag = False
        
        # Data Collection
        self.SENSOR_COUNT = 23
        self.csPosition = self.SENSOR_COUNT * 2
        self.connection_established = False

        # Setup serial port
        self.ser = serial.Serial(
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
        
        self.byteArray = []

    def checkByteArray(self, bArray):
        newArray = []
        checksum = 0

        chkPos = self.SENSOR_COUNT

        # Forms an array of 0 to 22 since sensorcount is 23(46)
        for counter in range (0, chkPos):
            byte1 = bArray[counter * 2]
            checksum = checksum ^ (int.from_bytes(byte1, byteorder="big", signed=True))
            byte2 = bArray[counter * 2 + 1]
            checksum = checksum ^ (int.from_bytes(byte2, byteorder="big", signed=True))
            combinedValue = int.from_bytes(byte2 + byte1, byteorder="big", signed=True)
            newArray.append(combinedValue)

        for counter in range (19,22):
            newArray[counter] /= 100

        newArray[22] /= 1000

        self.dataList = newArray[19:23]
        self.client.updateData(self.dataList)
        
        arrayChecksum = (int.from_bytes(bArray[self.csPosition] , byteorder="big", signed=True))
        # checksum is at 46th position of bArray
        # if checksum matches, then data is clean and ready to be stored into circular buffer
        if (checksum == arrayChecksum):
            self.ser.write(b'C')
            
            if checksum == 0:
                return
            
            self.buffer.append(newArray[0:19])
            return
        else:
            self.ser.write(b'N')
            
            print("Checksum error")
            print(bArray)
            print(newArray)
            print(checksum)
            print(arrayChecksum)
            
            return
    
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
        # will be receiving 47 array bytes, 0 to 46
        while (len(self.byteArray) < 47):
            startTime = time.time()
            while(self.ser.in_waiting == 0):
                currentTime = time.time()
                if (currentTime - startTime >= 2.0):
                    self.byteArray = []
                    self.connection_established = False
                    print('termination')
                    return

            rcv = self.ser.read()
            self.byteArray.append(rcv)

        self.checkByteArray(self.byteArray)    
        self.byteArray = []
           
    def communicate(self):
        if not self.connection_established:
            self.establish_connection()
        else:
            self.read_data()

    def processData(self, feedingBuffer):
        newPrediction = self.model.detectMove(feedingBuffer)

        if(newPrediction is None):
            print('ML returning None')
            return 'IDLE_A'

        return newPrediction

    def main(self):
        try:
            self.executionTime = time.time()
            while True:
                # Collect data
                self.communicate()
                
                if self.flushFlag and (self.buffer.getSize() == 80):
                    self.buffer.reset()
                    self.flushFlag = False
                    print('Buffer Flushed')
                
                if(self.buffer.getSize() == self.WINDOWSIZE):
                    print('Process Data')
                    currentTime = time.time()
                    if((currentTime - self.executionTime) >= self.FlushTime):
                        
                        action = 'IDLE_A'

                        tempBuffer = self.buffer.get()
                        feedingBuffer = []

                        for i in range(0, self.WINDOWSIZE):
                            feedingBuffer += tempBuffer[i]
                        
                        action = self.processData(feedingBuffer)
                        print(action)
                        
                        if self.movesSent >= 40:
                            if action == 'LOGOUT':
                                self.client.sendMessage(action)
                                print('Program End: LOGOUT & 41 MOVES SENT')
                                sys.exit(1)

                        if action == 'UNSURE':
                            self.FlushTime = 1.0
                        elif action != 'IDLE_A' and action != 'LOGOUT':
                            self.client.sendMessage(action)
                            self.movesSent += 1
                            self.FlushTime = 2.0
                            self.flushFlag = True

                        self.executionTime = currentTime
                        
                    self.buffer.reset()
                    
        except KeyboardInterrupt:
            print('Program End')
            sys.exit(1)           

if __name__ == '__main__':
    host = sys.argv[1]
    port = sys.argv[2]
    pi = Pi(host, port)
    pi.main()