
class DataStream:
    def __init__(self, data = None):
        self.data = data
        self.index = 0

    def setData(self, data):
        self.data = data
        self.index = 0

    def readData(self, count):
        end = min(len(self.data), self.index + count)
        return_data = self.data[self.index : end]
        self.index = end
        return return_data
