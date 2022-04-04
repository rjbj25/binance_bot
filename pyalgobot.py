import pytradeautomate.config as config
from binance.client import Client
from binance.enums import *
import time
import math
import datetime
import numpy as np
import pandas as pd
import talib as ta

from pyalgotrade import strategy
from pyalgotrade.barfeed import yahoofeed
from pyalgotrade.technical import ma
from pyalgotrade.technical import bollinger

class BBStrategy(strategy.BacktestingStrategy):
    def __init__(self, feed, instrument, smaPeriod):
        super(BBStrategy, self).__init__(feed, cash_or_brk=1000)
        self.__position = None
        self.__instrument = instrument
        # We'll use adjusted close values instead of regular close values.
        self.setUseAdjustedValues(True)
        self.__sma = ma.SMA(feed[instrument].getPriceDataSeries(), smaPeriod)
        self.__bb = bollinger.BollingerBands(feed[instrument].getPriceDataSeries(),smaPeriod,2)

    def onEnterOk(self, position):
        execInfo = position.getEntryOrder().getExecutionInfo()
        self.info("BUY at $%.2f" % (execInfo.getPrice()))

    def onEnterCanceled(self, position):
        self.__position = None

    def onExitOk(self, position):
        execInfo = position.getExitOrder().getExecutionInfo()
        self.info("SELL at $%.2f" % (execInfo.getPrice()))
        self.__position = None

    def onExitCanceled(self, position):
        # If the exit was canceled, re-submit it.
        self.__position.exitMarket()

    def onBars(self, bars):
        # Wait for enough bars to be available to calculate a SMA.
        if self.__sma[-1] is None:
            return
        
        if self.__bb is None:
            return

        bar = bars[self.__instrument]
        # If a position was not opened, check if we should enter a long position.
        close = bar.getClose()
        broker = self.getBroker()
        cash = broker.getCash()
        risky_cash = cash / 2
        quantity = risky_cash / close
        self.info(f'Cantidad de dinero {cash}')
        self.info(f'Banda inferior {self.__bb.getMiddleBand()[-1]}')
        self.info(f'El precio actual es: {bar.getPrice()}')
        self.info(f'**************************************')

        if self.__position is None:
            if bar.getPrice() <= self.__bb.getLowerBand()[-1]:
                # Enter a buy market order for 10 shares. The order is good till canceled.
                self.__position = self.enterLong(self.__instrument, quantity, True)
        # Check if we have to exit the position.
        elif bar.getPrice() > self.__bb.getUpperBand()[-1] and not self.__position.exitActive():
            self.__position.exitMarket()


def run_strategy(smaPeriod):
    client = Client(config.API_KEY, config.API_SECRET, tld='com')
    symbolTicker = config.SYMBOL
    buyQty = config.BUYQTY

    klines = client.get_historical_klines(symbolTicker, Client.KLINE_INTERVAL_1DAY, f"500 day ago UTC")
    df_klines = pd.DataFrame(klines)
    df_data = pd.DataFrame()
    df_data['Date'] = df_klines.apply(lambda x: datetime.datetime.fromtimestamp(float(x[0])/1000).strftime("%Y-%m-%d"), axis=1)
    df_data['Open'] = df_klines.apply(lambda x: float(x[1]) ,axis=1)
    df_data['High'] = df_klines.apply(lambda x: float(x[2]) ,axis=1)
    df_data['Low'] = df_klines.apply(lambda x: float(x[3]) ,axis=1)
    df_data['Close'] = df_klines.apply(lambda x: float(x[4]) ,axis=1)
    df_data['Volume'] = df_klines.apply(lambda x: float(x[5]) ,axis=1)
    df_data['Adj Close'] = df_klines.apply(lambda x: float(x[4]) ,axis=1)

    df_data.to_csv('data.csv')

    # Load the bar feed from the CSV file
    feed = yahoofeed.Feed()
    feed.addBarsFromCSV("orcl", "data.csv")

    # Evaluate the strategy with the feed.
    myStrategy = BBStrategy(feed, "orcl", smaPeriod)
    myStrategy.run()
    print("Final portfolio value: $%.2f" % myStrategy.getBroker().getEquity())


if __name__ == "__main__":
    run_strategy(15)
