import config
from binance.client import Client
from binance.enums import *
import time
import math
import datetime
import numpy as np
import pandas as pd
import talib as ta

client = Client(config.API_KEY, config.API_SECRET, tld='com')
symbolTicker = config.SYMBOL
buyQty = config.BUYQTY

def main():
    while True:
        klines_15_min_20_periods = client.get_historical_klines(symbolTicker, Client.KLINE_INTERVAL_15MINUTE, f"15 hour ago UTC")
        klines_1min = client.get_historical_klines(symbolTicker, Client.KLINE_INTERVAL_1MINUTE, f"'1' minute ago UTC")
        bb_20_15min = _bb(klines_15_min_20_periods)
        try:
            current_price = get_curren_price(klines_1min)
        except Exception as e:
            print(e)
            continue
        tendencia = get_tendencia()
        print(f'***** La tendencia es {tendencia}')
        print(f'***** Bandas de bollinger {bb_20_15min}')
        print(f'***** Precio actual {current_price}')
        if  no_orders():
            if tendencia=='Ascendente':
                if strategy_bb(bb_20_15min, current_price):
                    orden = put_order()
                else:
                    print('No hay punto de entrada')
            else:
                print('No hay tendencia ascendente')
        else:
            print('Hay ordenes pendientes por cerrar')

        time.sleep(1)

def get_tendencia():
    klines = client.get_historical_klines(symbolTicker, Client.KLINE_INTERVAL_4HOUR, f"168 hour ago UTC")
    df_klines = pd.DataFrame(klines)
    df_klines['closed_price'] = df_klines.apply(lambda x: float(x[4]) ,axis=1)
    sma = ta.SMA(df_klines['closed_price'].values, timeperiod=20)
    sma_actual = sma[len(sma)-1]
    sma_anterior = sma[len(sma)-2]
    if sma_actual > sma_anterior:
        return 'Ascendente'
    else:
        return 'Descendente'


def no_orders():
    pass


def strategy_bb(bb_20_15min, current_price, tendencia):
    if current_price <= bb_20_15min['stddown']:
        return True
    else:
        return False


def _bb(klines_15_min_20_periods):
    df_15_min_20_periods = pd.DataFrame(klines_15_min_20_periods)
    df_15_min_20_periods['closed_price'] = df_15_min_20_periods.apply(lambda x: float(x[4]) ,axis=1)
    stdup, mean, stddown = ta.BBANDS(df_15_min_20_periods['closed_price'].values, 
        timeperiod=20, nbdevup=2, nbdevdn=2, matype=0)
    stdup = stdup[len(stdup)-1]
    mean = mean[len(mean)-1]
    stddown = stddown[len(stddown)-1]
    bb = {'mean':mean,'stdup':stdup,'stddown':stddown}
    return bb


def get_curren_price(klines):
    df_klines = pd.DataFrame(klines)
    return df_klines[4].iloc[-1]


def orderStatus(orderToCkeck):
    try:
        status = client.get_order(
            symbol = symbolTicker,
            orderId = orderToCkeck.get('orderId')
        )
        return status.get('status')
    except Exception as e:
        print(e)
        return 7

def put_order(price):
    buyOrder = client.create_order(
            symbol=symbolTicker,
            side='BUY',
            type='STOP_LOSS_LIMIT',
            quantity=buyQty,
            price='{:.8f}'.format(round(price)),
            stopPrice='{:.8f}'.format(round(price)),
            timeInForce='GTC')
    

if __name__ == "__main__":
    main()
