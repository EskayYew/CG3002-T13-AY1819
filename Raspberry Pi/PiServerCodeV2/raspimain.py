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
        print(bufferY)
        return 'chicken'

    def processAction(self):
        self.databuffer = self.buffer.get()

        # machine learning will iterate through databuffer and determine action
        action = self.processData(self.databuffer)

        processLock.acquire()
        print(action)
        self.sender.sendMessage(action)
        processLock.release()

        self.buffer.reset()
        self.databuffer = []
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

            # must lock when feeding data to buffer. 
            processLock.acquire()
            self.buffer.append(self.data_buff)
            processLock.release()
            
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


class Communication:

    def __init__(self, host, port):
        self.host = host
        self.port = int(port)
        self.bs = 16
        self.key = bytes("1234123412341234".encode("utf8"))
        
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
        return '#{}|4.65|2|1.988|10|'.format(self.actions[message])

    # message can be replaced by a list containing action and calculation values in future
    def sendMessage(self, message):
        message = self.format(message)
        message = self.encrypt(message)
        self.client.send(message)    

class Pi:
    def __init__(self, host, port):
        self.dataList = [0, 0, 0, 0]
        self.threads = []
        self.buffer = CircleBuffer(50)
        self.client = Communication(host, port) 

    def main(self):
        SENSOR_COUNT = 5

        receiver = Receiver(SENSOR_COUNT, self.buffer)
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
