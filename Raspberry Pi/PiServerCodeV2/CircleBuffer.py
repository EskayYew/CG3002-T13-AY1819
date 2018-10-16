class CircleBuffer():
    def __init__(self, bufferSize):
        self.size = bufferSize
        self.buffer = [None]*bufferSize
        self.curr = 0
        self.currSize = 0

    def append(self, x):
        self.buffer[self.curr] = x
        self.curr = (self.curr + 1) % self.size
        if (self.currSize < self.size):
            self.currSize += 1

    # Returns a list of oldest set of data to newest set of data.
    def get(self):
        return self.buffer[:self.currSize]

    def getSize(self):
        return self.currSize

    # Use reset after machine learning algo
    def reset(self):
        self.buffer = [None]*self.size
        self.curr = 0
        self.currSize = 0
