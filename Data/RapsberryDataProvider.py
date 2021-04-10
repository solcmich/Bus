import json
import os
import threading
import time

import pandas as pd

from Data.Storage.ColdStorage import ColdStorage
from Sensors.SenseHat.SenseHat import CSenseHat

""" Master class for storage """
"""
Basically runs all the storages needed and provides the option to perform "hot update"
hot update is triggered by some event from outside in order to maintain maximum timeliness
"""


class SenseHatDataProvider:
    def __init__(self, root_storage_path):
        self.sense_hat_storage = dict()
        self.gps_storage = dict()

        self.root_storage_path = root_storage_path
        self.sense_hat = CSenseHat()


    """ Public api """

    def run(self):
        """
        Isn't it obvious?
        """
        self.__run_sense_hat_storage()

    def get_temperature(self):
        """
        :return klines for given pair, or for every pair when pair is not specified
        """
        return self._get(self.sense_hat_storage, 'temperature')

    def get_accelerometer(self):
        """
        :return balance for given symbol, or for every pair when pair is not specified
        """
        return self._get(self.sense_hat_storage, 'accelerometer')

    def get_gyroscope(self):
        """
        :return klines for given pair, or for every pair when pair is not specified
        """
        return self._get(self.sense_hat_storage, 'gyroscope')

    def get_pressure(self):
        """
        :return klines for given pair, or for every pair when pair is not specified
        """
        return self._get(self.sense_hat_storage, 'pressure')

    def get_humidity(self):
        """
        :return klines for given pair, or for every pair when pair is not specified
        """
        return self._get(self.sense_hat_storage, 'humidity')

    def _get(self, storage, pair):
        pass

    def __run_sense_hat_storage(self):
        e = threading.Event()
        sensors = ['temperature', 'humidity', 'accelerometer', 'pressure', 'gyroscope']
        dirname_temperature = os.path.join(self.root_storage_path, f'SenseHat/Temperature/data.csv')
        dirname_humidity = os.path.join(self.root_storage_path, f'SenseHat/Humidity/data.csv')
        s_temperature = ColdStorage(dirname_temperature)
        s_humidity = ColdStorage(dirname_humidity)
        while True:
            s_temperature.append(self.sense_hat.get_temperature())
            s_humidity.append(self.sense_hat.get_humidity())
            time.sleep(10)


