import serial
#use https://github.com/eric-wieser/numpy_ringbuffer

SENSOR_COUNT = 5
msg_len = (2 * SENSOR_COUNT) + 1 

# Setup serial port
ser = serial.Serial('COM5', 115200)

#while(True):
# Wait for SYNC packet
while(ser.read() != b'0'):
    pass
print("connection with arduino established")
ser.write(b'1')
# Wait for SYNC-ACK packet
while(ser.read() != b'2'):
    pass
data_buff = []
chksum = b'0'
is_id = True
while (len(data_buff) < msg_len):
    data = ser.read()
    if (data != b'\r' and data != b'\n'):
        print(data.decode('utf-8'))
        if not is_id:
            chksum = bytes(x ^ y for x, y in zip(chksum, data))
        data_buff.append(data)
        is_id = not is_id
# print(chksum)
# print(data_buff)
if ((data_buff[msg_len - 1]).decode() == str(ord(chksum))):
    print("Data received and verified")
    ser.write(b'1')
else:
    ser.write(b'6')
    print("Checksum error")
    print('expected: {} recv: {}'.format(data, chksum))
# Wait for FIN packet
while(ser.read() != b'7'):
    pass
ser.write(b'7')
while(ser.read() != b'1'):
    pass
print("Message received")
print(data_buff)
