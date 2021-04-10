import json
import os
import threading

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
        """
        Initializes new storage manager with help of configuration.
        Should only be one instance in running app
        """
        with open('../config.json') as config_file:
            config = json.load(config_file)

        self.default_pairs = config["binance"]["default_pairs"]
        self.default_futures_pairs = config["binance"]["default_futures_pairs"]
        self.default_time_frames = config["binance"]["default_time_frames"]
        self.default_symbols = config['binance']['default_symbols']
        self.client = client
        self.hot_events = dict()

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

    def invoke_hot_event(self, symbol, event_type):
        """
        Entry point for hot event execution
        """
        self.hot_events[(event_type, symbol)].set()

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

    def get_futures_trades(self, pair=None):
        """
        :return futures trades for given pair, or for every pair when pair is not specified
        """
        return self._get(self.futures_trades_storage, pair)


    @staticmethod
    def _get(storage, pair):
        if pair is None:
            return pd.concat([x.get() for x in storage.values()])
        return storage[pair].get()

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

        # todo: Handle initial load
        # s.initial_load(self.client.get_historical_klines, symbol=p, interval=tf, start_str='1600000000000')


    def __run_spot_trades_storage(self):
        for p in self.default_pairs:
            e = threading.Event()
            self.hot_events[("spot_trades", str(p))] = e
            dirname = os.path.join(self.root_storage_path, f'Spot/Trades/{p}/data.csv')
            s = SelfUpdatedStorage(dirname, self.client.get_my_trades, e, symbol=p)
            s.start()
            self.spot_trades_storage[p] = s

    def __run_spot_orders_storage(self):
        for p in self.default_pairs:
            e = threading.Event()
            self.hot_events[("spot_orders", str(p))] = e
            dirname = os.path.join(self.root_storage_path, f'Spot/Orders/{p}/data.csv')
            s = SelfUpdatedStorage(dirname, self.client.get_all_orders, e, symbol=p)
            s.start()
            self.spot_orders_storage[p] = s

    def __run_spot_open_orders_storage(self):
        for p in self.default_pairs:
            e = threading.Event()
            self.hot_events[("spot_open_orders", str(p))] = e
            dirname = os.path.join(self.root_storage_path, f'Spot/OpenOrders/{p}/data.csv')
            s = SelfUpdatedStorage(dirname, self.client.get_open_orders, e, symbol=p)
            s.start()
            self.spot_open_orders_storage[p] = s

    def __run_futures_trades_storage(self):
        for p in self.default_futures_pairs:
            e = threading.Event()
            self.hot_events[("futures_trades", str(p))] = e
            dirname = os.path.join(self.root_storage_path, f'Futures/Trades/{p}/data.csv')
            s = SelfUpdatedStorage(dirname, self.client.futures_get_my_trades, e, symbol=p)
            s.start()
            self.futures_trades_storage[p] = s

    def __run_futures_orders_storage(self):
        for p in self.default_futures_pairs:
            e = threading.Event()
            self.hot_events[("futures_orders", str(p))] = e
            dirname = os.path.join(self.root_storage_path, f'Futures/Orders/{p}/data.csv')
            s = SelfUpdatedStorage(dirname, self.client.futures_get_all_orders, e, symbol=p)
            s.start()
            self.futures_orders_storage[p] = s

    def __run_balance_storage(self):
        e = threading.Event()
        self.hot_events["balance"] = e
        for p in self.default_symbols:
            dirname = os.path.join(self.root_storage_path, f'Balance/{p}/data.csv')
            s = SelfUpdatedStorage(dirname, self.client.get_balance, e, asset=p)
            s.start()
            self.balance_storage[p] = s

    def __run_hot_candles_storage(self):
        for p in self.default_pairs:
            s = CandlesHotStorage(p)
            self.candles_hot_storage[p] = s
            self.client.subscribe_kline_price(p, s.save)

    def __run_trading_rules_storage(self):
        e = threading.Event()
        for p in self.default_pairs:
            dirname = os.path.join(self.root_storage_path, f'Rules/{p}/data.csv')
            s = SelfUpdatedStorage(dirname, self.client.get_symbol_info, e, symbol=p)
            s.start()

    def on_order_change(self, **params):
        print(f'Order status changed for {params["pair"]}')
        self.hot_events[('spot_orders', params['pair'])].set()
        self.hot_events[('spot_open_orders', params['pair'])].set()
        self.hot_events[('spot_trades', params['pair'])].set()
        self.hot_events['balance'].set()
