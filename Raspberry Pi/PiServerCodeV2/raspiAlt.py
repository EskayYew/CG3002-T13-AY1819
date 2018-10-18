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
   
    def processData(self, bufferY):
        #print('Machine Learning')
        return 'chicken'

    def processAction(self):
        self.databuffer = self.buffer.get()

        # machine learning will iterate through databuffer and determine action
        # if(self.buffer.getSize == 250):
        action = self.processData(self.databuffer)

        # process lock required so as to prevent any corruption of any the sent data to server.
        processLock.acquire()
        print(action)
        self.sender.sendMessage(action)
        processLock.release()

        # need to create a flag so if action is sent then we reset the buffer.
        self.buffer.reset()
        self.databuffer = []
        threading.Timer(2, self.processAction).start()

    # suppose to start after 60 seconds. 5 is dummy value for testing.
    def run(self):
        threading.Timer(5, self.processAction).start()

class Receiver(threading.Thread):
    def __init__(self, bufferX, dataList, computeList):
        threading.Thread.__init__(self)

        # current: 25, need to add 4 for dataList
        self.SENSOR_COUNT = 25
        
        self.buffer = bufferX
        self.dataList = dataList
        self.computeList = computeList

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

        # self.ser.reset_input_buffer()
        # self.ser.reset_output_buffer()
        
        self.data_buff = []
        self.byteArray = []

    def checkByteArray(self, bArray):
        newArray = []
        checksum = 0

        chkPos = self.SENSOR_COUNT

        # go from 0 to 24 since sensorcount is 25(50,51)
        for counter in range (0, chkPos):
            byte1 = bArray[counter * 2]
            checksum = checksum ^ (int.from_bytes(byte1, byteorder="big", signed=True))
            byte2 = bArray[counter * 2 + 1]
            checksum = checksum ^ (int.from_bytes(byte2, byteorder="big", signed=True))
            combinedValue = int.from_bytes(byte2 + byte1, byteorder="big", signed=True)
            
            newArray.append(combinedValue)

        chkPos = chkPos*2

        # checksum is at 50th position of bArray
        # if checksum matches, then data is clean and ready to be stored into circular buffer
        if (checksum == (int.from_bytes(bArray[chkPos] , byteorder="big", signed=True))):            
            self.ser.write(b'1')
            # print("success")
            return newArray
        else:
            self.ser.write(b'6')
            print("Checksum error")
            print(self.byteArray)
            print(newArray)
            return None

    def communicate(self):

        # Wait for SYNC packet
        while(self.ser.read() != b'\x00'):
            pass
        self.ser.write(b'1')
        # Wait for SYNC-ACK packet
        while(self.ser.read() != b'\x02'):
            pass

        #print("Starting data tranfser...")
        # handshake established with handshake flag

        #will be receiving 52 array bytes, 0 to 51
        while (len(self.byteArray) < 51):
            rcv = self.ser.read()
            if (rcv != b'\r' and rcv != b'\n'):
                self.byteArray.append(rcv)
        self.data_buff = self.checkByteArray(self.byteArray)
        
        #need to be changed to 25:26
        self.computeList = self.data_buff[23:24]

        if(self.data_buff is not None):
            processLock.acquire()
            self.buffer.append(self.data_buff)
            processLock.release()

        # Wait for FIN packet
        while(self.ser.read() != b'\x07'):
            pass
        self.ser.write(b'7')
        while(self.ser.read() != b'\x01'):
            pass

        self.byteArray = []
        self.data_buff = []

    def receiveLoop(self):
        # newTime = time.time() + 5
        self.communicate()
        # threading.Timer(newTime - time.time(), self.printSelf).start()
        threading.Timer(0.05, self.receiveLoop).start()

    def run(self):
        self.receiveLoop()

class ComputeData:
    def __init__(self, dataList, computeList):
        threading.Thread.__init__(self)
        self.dataList = dataList
        self.computeList = computeList
        self.prevTime = time.time()
        self.energy = 0.00

    def compute(self):
        # voltage
        self.dataList[0] = self.computeList[0] * 2.0 * 4.875 / 1024.0
        # current
        self.dataList[1] = self.computeList[1] * 4.875 / 1024.0
        # power
        power = self.dataList[0] * self.dataList[1]
        self.dataList[2] = power

        currentTime = time.time()

        # energy
        self.energy += self.energy + ((power * (currentTime - self.prevTime)) / 3600.0)
        self.dataList[3] = self.energy
        self.prevTime = currentTime

    def computeLoop(self):
        # newTime = time.time() + 5
        self.compute()
        # threading.Timer(newTime - time.time(), self.printSelf).start()
        threading.Timer(0.05, self.computeLoop).start()

    def run(self):
        self.prevTime = time.time()
        self.computeLoop()

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

    # format thrown with dummy values
    # To replace values of voltage, current, power, cumpower       
    def format(self, message):
        return '#{}|{0:.2f}|{0:.2f}|{0:.2f}|{0:.2f}|'.format(self.actions[message], self.dataList[0], self.dataList[1], self.dataList[2], self.dataList[3])

    # message can be replaced by a list containing action and calculation values in future
    def sendMessage(self, message):
        message = self.format(message)
        message = self.encrypt(message)
        self.client.send(message)    

class Pi:
    def __init__(self, host, port):
        self.dataList = [1.65, 3.00, 1.98, 10.00]
        self.threads = []
        self.buffer = CircleBuffer(250)
        self.client = Communication(host, port, self.dataList)
        self.computeList = [4.65, 2.00]

    def main(self):
        receiver = Receiver(self.buffer, self.dataList, self.computeList)
        machine = MachineLearning(self.buffer, self.client)
        calculator = ComputeData(self.dataList, self.computeList)

        self.threads.append(machine)
        self.threads.append(receiver)
        self.threads.append(calculator)

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