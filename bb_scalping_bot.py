import config
from binance.client import Client
from binance.enums import *
import time
import math
import datetime
import numpy as np
import pandas as pd

client = Client(config.API_KEY, config.API_SECRET, tld='com')
symbolTicker = config.SYMBOL
symbolPrice = 0
ma50 = 0
auxPrice = 0.0
buyQty = config.BUYQTY

def main():
    while True:
        time.sleep(3)
        bb_20_15min = _bb_15min('7.5')


def _bb_15min(time):
    klines = client.get_historical_klines(symbolTicker, Client.KLINE_INTERVAL_15MINUTE, f"{time} hour ago UTC")
    df_klines = pd.DataFrame(klines)

    df_klines['closed_price'] = df_klines.apply(lambda x: float(x[4]) ,axis=1)
    media = df_klines["closed_price"].mean()
    std_up = df_klines["closed_price"].mean()+(df_klines["closed_price"].std()*2)
    std_down = df_klines["closed_price"].mean()-(df_klines["closed_price"].std()*2)

    print(f'Media: {media}')
    print(f'Dvest +: {std_up}')
    print(f'Dvest -: {std_down}')

    bb = {
        'media':media,
        'std_up':std_up,
        'std_down':std_down
    }
    return bb

if __name__ == "__main__":
    main()