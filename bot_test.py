import config
from binance.client import Client
from binance.enums import *
import time
import math
import datetime
import numpy as np

client = Client(config.API_KEY, config.API_SECRET, tld='com')
symbolTicker = config.SYMBOL
symbolPrice = 0
ma50 = 0
auxPrice = 0.0
buyQty = config.BUYQTY


def _ma20_():
    ma20_local = 0
    sum = 0

    klines = client.get_historical_klines(symbolTicker, Client.KLINE_INTERVAL_15MINUTE, "15 hour ago UTC")

    if (len(klines) == 60):

        for i in range(10,60):
            sum = sum + float(klines[i][4])

        ma20_local = sum / 20

    return ma20_local


while True:
    
    pass

