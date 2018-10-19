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

class Receiver(threading.Thread):
    def __init__(self, bufferX):
        threading.Thread.__init__(self)
        
        self.SENSOR_COUNT = 23
        self.energy = 0.000
        self.buffer = bufferX
        self.connection_established = False
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

        # go from 0 to 24 since sensorcount is 25(50,51)
        for counter in range (0, chkPos):
            byte1 = bArray[counter * 2]
            checksum = checksum ^ (int.from_bytes(byte1, byteorder="big", signed=True))
            byte2 = bArray[counter * 2 + 1]
            checksum = checksum ^ (int.from_bytes(byte2, byteorder="big", signed=True))
            combinedValue = int.from_bytes(byte2 + byte1, byteorder="big", signed=True)
            #checksum = combinedValue ^ checksum
            
            if counter >= 19 and counter <= 21:
                combinedValue /= 100
            if counter == 22:
                combinedValue /= 1000
            
            newArray.append(combinedValue)

        self.energy += newArray[22]

        newArray[22] = self.energy
        
        chkPos = chkPos*2

        arrayChecksum = (int.from_bytes(bArray[chkPos] , byteorder="big", signed=True))
        # checksum is at 50th position of bArray
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
        #self.ser.reset_input_buffer()
        #self.ser.reset_output_buffer()
        self.connection_established = True
        print("Connection Established")
    
    def read_data(self):
        #will be receiving 52 array bytes, 0 to 51
        while (len(self.byteArray) < 47):
            startTime = time.time()
            while(self.ser.in_waiting == 0):
                currentTime = time.time()
                if (currentTime - startTime >= 2.0):
                    self.byteArray = []
                    self.data_buff = []
                    self.connection_established = False
                    #self.ser.reset_input_buffer()
                    #self.ser.reset_output_buffer()
                    print('termination')
                    return
                
            rcv = self.ser.read()
            self.byteArray.append(rcv)
        #    if (rcv != b'\r' and rcv != b'\n'):
        #        self.byteArray.append(rcv)
                
                
        self.data_buff = self.checkByteArray(self.byteArray)
        
        if(self.data_buff is not None):
            processLock.acquire()
            self.buffer.append(self.data_buff)
            processLock.release()
            
        if(self.buffer.getSize() % 25 == 0):
            print(self.buffer.getSize())

        #self.ser.reset_input_buffer()
        self.byteArray = []
        self.data_buff = []
           
    def communicate(self):
        if not self.connection_established:
            self.establish_connection()
            #self.read_data()
        else:
            self.read_data()
        #print("Starting data tranfser...")
        # handshake established with handshake flag

    def receiveLoop(self):
        # newTime = time.time() + 5
        while True:
            self.communicate()
        # threading.Timer(newTime - time.time(), self.printSelf).start()
        #threading.Timer(0.02, self.receiveLoop).start()

    def run(self):
        self.receiveLoop()

class Pi:
    def __init__(self):
        self.dataList = [0, 0, 0, 0]
        self.threads = []
        self.buffer = CircleBuffer(750)

    def main(self):
        try:
            receiver = Receiver(self.buffer)
            
            # machine = MachineLearning(self.buffer)

            # self.threads.append(machine)
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