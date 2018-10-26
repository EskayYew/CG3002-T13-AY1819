import time
import serial
import csv
import sys
from CircleBuffer import CircleBuffer

class Pi:
    def __init__(self):
        self.WINDOWSIZE = 2000
        self.buffer = CircleBuffer(self.WINDOWSIZE)
        self.fileName = str(sys.argv[1])
        self.SENSOR_COUNT = 23
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

        # go from 0 to 22 since sensorcount is 23(46)
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
        
        chkPos = chkPos*2

        arrayChecksum = (int.from_bytes(bArray[chkPos] , byteorder="big", signed=True))
        # checksum is at 46th position of bArray
        # if checksum matches, then data is ready to be stored into circular buffer
        if (checksum == arrayChecksum):            
            self.ser.write(b'C')

            if checksum == 0:
                return None

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
            self.buffer.append(self.data_buff)
            
        if(self.buffer.getSize() % 50 == 0):
            print(self.buffer.getSize())

        self.byteArray = []
        self.data_buff = []
           
    def communicate(self):
        if not self.connection_established:
            self.establish_connection()
        else:
            self.read_data()
        
    def recordData(self):
        file = self.fileName
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

    def main(self):
        try:
            while True:
                self.communicate()
                if(self.buffer.getSize == self.WINDOWSIZE):
                    self.recordData()
        except KeyboardInterrupt:
            self.recordData()

if __name__ == '__main__':
    pi = Pi()
    pi.main()