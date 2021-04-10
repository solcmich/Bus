from sense_hat import SenseHat
from datetime import datetime

class CSenseHat:
    def __init__(self):
        self.hat = SenseHat()

    @staticmethod
    def _get(functor):
        ret = pd.DataFrame()
        ret.date = [datetime.now()]
        ret.Value = [functor()]
        return ret

    def get_temperature(self):
        return _get(self.hat.get_temperature())

    def get_accelerometer(self):
        return _get(self.hat.get_accelerometer())

    def get_gyroscope(self):
        return _get(self.hat.get_gyroscope())

    def get_pressure(self):
        return _get(self.hat.get_pressure())

    def get_humidity(self):
        return _get(self.hat.get_humidity())

