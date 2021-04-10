from Data.SenseHatDataProvider import SenseHatDataProvider
from Data.GpsDataProvider import GpsDataProvider
if __name__ == '__main__':
    sense = SenseHatDataProvider('.')
    sense.run()
    gps = GpsDataProvider('.')
    gps.run()


