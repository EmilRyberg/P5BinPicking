from pyurg import pyurg

LOW_THRESHOLD = 100
HIGH_THRESHOLD = 1000

class LaserScanner:
    def __init__(self):
        self.ignore_indexes = []
        self.person_close = False

        self.scanner = pyurg.UrgDevice()
        if not self.scanner.connect():
            print('Could not connect to laser scanner.')
            exit(0)

        #Getting reference values to ignore
        data, timestamp = self.scanner.capture()
        for i in range(len(data)):
            if LOW_THRESHOLD < data[i] < HIGH_THRESHOLD and LOW_THRESHOLD < data[i + 1] < HIGH_THRESHOLD and LOW_THRESHOLD < data[i + 2] < HIGH_THRESHOLD:
                self.ignore_indexes.append(i)

    def check_distances(self):
        while True:
            data, timestamp = self.scanner.capture()
            print("New capture")
            if timestamp == -1:
                print('Could not get laser scanner data')
                exit(0)
            else:
                for i in range(len(data)):
                    if i == len(data)-2:
                        return
                    elif i in self.ignore_indexes or i+1 in self.ignore_indexes or i-1 in self.ignore_indexes:
                        continue
                    elif LOW_THRESHOLD < data[i] < HIGH_THRESHOLD and LOW_THRESHOLD < data[i+1] < HIGH_THRESHOLD and LOW_THRESHOLD < data[i+2] < HIGH_THRESHOLD:
                        self.person_close = True
                        return self.person_close



if __name__ == "__main__":
    laser_scanner = LaserScanner()
    while True:
        laser_scanner.check_distances()