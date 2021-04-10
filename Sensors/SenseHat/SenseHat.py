from sense_hat import SenseHat
from datetime import datetime
import pandas as pd

class CSenseHat:
    def __init__(self):
        self.hat = SenseHat()

    def _get(self, f):
        ret = pd.DataFrame()
        ret.index = [datetime.timestamp(datetime.now())]
        ret['Value'] = [f()]
        return ret

    def get_temperature(self):
        return self._get(self.hat.get_temperature)

    def get_accelerometer(self):
        return self._get(self.hat.get_accelerometer)

    def get_gyroscope(self):
        return self._get(self.hat.get_gyroscope)

    def get_pressure(self):
        return self._get(self.hat.get_pressure)

    def get_humidity(self):
        return self._get(self.hat.get_humidity)

