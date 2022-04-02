import config
from binance.client import Client
import pandas as pd

class Feed:
    def __init__(self, symbol, interval, limit):
        self.__client = Client(config.API_KEY, config.API_SECRET, tld='com')
        self.__klines = self.__client.get_klines(symbol=symbol, interval=interval, limit=limit)
        
    def get_df_klines(self):
        return pd.DataFrame(self.__klines)

    def get_Client(self):
        return self.__client

    def to_csv(self, filename):
        self.__df_klines.to_csv(filename)