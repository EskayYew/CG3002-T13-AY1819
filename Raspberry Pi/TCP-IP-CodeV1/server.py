import sys
import socket


def main():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    host = socket.gethostname()
    ip = socket.gethostbyname(host)
    port = 12345

    try:
        s.bind((ip, port))

    except socket.error as msg:
        print('Bind failed. Error Code : ' + str(msg[0]) + ' Message ' + msg[1])
        sys.exit()

    print("[+] Socket bind success.p")
    s.listen(1)

    print("[+] Currently listening on", ip + ":" + str(port))
    c, address = s.accept()
    print("[+] Connection incoming from:", address)

    while True:
        data = c.recv(1024)
        if not data:
            break
        data = data.decode('utf-8')
        print("[+] Message from connected user:", data)

        print("[+] Sending to connected user: ", data)
        c.send(data.encode())

    c.close()


if __name__ == '__main__':
    main()



