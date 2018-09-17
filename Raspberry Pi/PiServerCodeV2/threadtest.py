import threading
import time

# Applying threading on different processes between classes
# Credits to https://stackoverflow.com/questions/17774768/python-creating-a-shared-variable-between-threads
# Absolutely necessary if you are doing different processes

processLock = threading.Lock()

class Sender(threading.Thread):
    def __init__(self, name, size):
        threading.Thread.__init__(self)
        self.name = name
        self.size = size

    def printSelf(self):
        processLock.acquire()
        print('I am the ', self.name)
        processLock.release()
        threading.Timer(5, self.printSelf).start()

    def run(self):
        threading.Timer(1, self.printSelf).start()

class Receiver(threading.Thread):
    def __init__(self, name):
        threading.Thread.__init__(self)
        self.name = name

    def printSelf(self):
        # newTime = time.time() + 5

        processLock.acquire()
        print('I am the ', self.name)
        processLock.release()

        # threading.Timer(newTime - time.time(), self.printSelf).start()
        threading.Timer(2, self.printSelf).start()

    def run(self):
        self.printSelf()
        
class Pi:
    def __init__(self):
        self.dataList = [0, 0, 0, 0]
        self.threads = []

    def main(self):

        sender = Sender("sender", 10)
        receiver = Receiver("receiver") 

        self.threads.append(sender)
        self.threads.append(receiver)

        for t in self.threads:
            t.daemon = True
            t.start()

        while True:
            time.sleep(0.01)

        print('Program End')

if __name__ == '__main__':
    pi = Pi()
    pi.main()