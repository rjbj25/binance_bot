import config as config
from binance.client import Client
import pandas as pd

class Feed:
    def __init__(self, symbol, interval, limit):
        self.__client = Client(config.API_KEY, config.API_SECRET, tld='com')
        self.__klines = self.__client.get_klines(symbol=symbol, interval=interval, limit=limit)
        self.start_date = None
        self.end_date = None
        self.symbol = symbol
        self.interval = interval

    def get_df_klines(self):
        return pd.DataFrame(self.__klines)

    def get_Client(self):
        return self.__client

    def to_csv(self, filename):
        self.__df_klines.to_csv(filename)

    def get_df_klines_interval(self):
        return pd.DataFrame(self.__client.get_klines(symbol=self.symbol, interval=self.interval, startTime = self.start_date, endTime = self.end_date))