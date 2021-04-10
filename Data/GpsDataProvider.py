import time
import board
import busio
import threading
import serial
import os
import pandas as pd
from datetime import datetime
import adafruit_gps

from Data.Storage.ColdStorage import ColdStorage
from Sensors.SenseHat.SenseHat import CSenseHat

""" Master class for storage """
"""
Basically runs all the storages needed and provides the option to perform "hot update"
hot update is triggered by some event from outside in order to maintain maximum timeliness
"""


class GpsDataProvider(threading.Thread):
    def __init__(self, root_storage_path):
        super().__init__()
        self.uart = serial.Serial("/dev/ttyS0", baudrate=9600, timeout=10)
        self.gps = adafruit_gps.GPS(self.uart)  # Use UART/pyserial
        self.gps.send_command(b"PMTK314,0,1,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0")
        self.gps.send_command(b"PMTK220,1000")
        self.sense_hat_storage = dict()
        self.gps_storage = dict()

        self.root_storage_path = root_storage_path
        self.sense_hat = CSenseHat()


    """ Public api """

    def run(self):
        """
        Isn't it obvious?
        """
        self.__run_gps_hat_storage()

    def get_longittude(self):
        """
        :return klines for given pair, or for every pair when pair is not specified
        """
        return self._get(self.sense_hat_storage, 'temperature')

    def get_latitude(self):
        """
        :return balance for given symbol, or for every pair when pair is not specified
        """
        return self._get(self.sense_hat_storage, 'accelerometer')

    def _get(self, storage, pair):
        pass

    def __run_gps_hat_storage(self):
        e = threading.Event()
        dirname_loc = os.path.join(self.root_storage_path, f'GPS/Location/data.csv')
        s_loc = ColdStorage(dirname_loc)
        last_print = time.monotonic()
        i = 0
        while True:

            self.gps.update()
            current = time.monotonic()
            if current - last_print >= 1.0:
                last_print = current
                if not self.gps.has_fix:
                    # Try again if we don't have a fix yet.
                    print("Waiting for fix...")
                    continue
            i += 1
            if i % 10 == 1:
                print('Got data from GPS')
            ret = pd.DataFrame()
            ret['Date'] = [datetime.timestamp(datetime.now())]
            ret['latitude'] = [self.gps.latitude]
            ret['longtitude'] = [self.gps.longitude]
            s_loc.append(ret)


