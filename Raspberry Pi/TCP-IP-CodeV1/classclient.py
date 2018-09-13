import socket
import sys
import base64
from Crypto import Random
from Crypto.Cipher import AES

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
        return s + (self.bs - len(s) % self.bs) * chr(self.bs - len(s) % self.bs)

    def format(self, message):
        return '#{}|4.65|2|1.988|10|'.format(self.actions[message])

    def communicate(self):
        message = input("Enter Move Name: ")
        while message != 'q':
            message = self.format(message)
            message = self.encrypt(message)
            self.client.send(message)
            message = input("Enter Move Name: ")

        self.client.close()


def main():
    host = sys.argv[1]
    port = sys.argv[2]

    client = Communication(host, port)
    client.communicate()


if __name__ == '__main__':
    main()
