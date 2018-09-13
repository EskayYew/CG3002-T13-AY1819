import socket


def main():
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    host = '172.20.10.5'
    port = 12345

    client.connect((host, port))

    print("[+] You are currently connected to ", host + ":" + str(port))

    message = input("Enter Message: ")
    while message != 'q':
        client.send(message.encode())
        data = client.recv(1024)
        data = data.decode('utf-8')
        print("[+] Received from server: " + str(data))
        message = input("Enter Message: ")

    client.close()


if __name__ == '__main__':
    main()
