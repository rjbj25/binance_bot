from feed import Feed as fd
from operation import Operation as op
from account import BacktestAccount as bac
import talib as ta
import pandas as pd
import datetime

'''This class implement a RSI trading strategy.'''

class Strategy:

    def __init__(self, symbol, client, klines):
        self.symbol = symbol
        self.client = client
        self.klines = klines
        self.bac_account = bac(1000, 'BUSD')
        self.balance_inicial = self.bac_account.account_balance
        self.current_balance = 0
        self.last_price = 0
        

    def backtestBB(self, timeperiod, nbdevup, nbdevdn):
        cnt_operations = 0
        win_rate = 0
        loss_rate = 0
        tendencia = None
        df_klines = pd.DataFrame(self.klines)
        df_klines['closed_price'] = df_klines.apply(lambda x: float(x[4]) ,axis=1)
        df_klines['lowest_price'] = df_klines.apply(lambda x: float(x[3]) ,axis=1)
        df_klines['higest_price'] = df_klines.apply(lambda x: float(x[2]) ,axis=1)
        stdup, mean, stddown = ta.BBANDS(df_klines['closed_price'].values, timeperiod=timeperiod, nbdevup=nbdevup, nbdevdn=nbdevdn, matype=0)
        rsi = ta.RSI(df_klines['closed_price'].values, timeperiod=timeperiod)
        ma100 = ta.SMA(df_klines['closed_price'].values, timeperiod=100)
        ma200 = ta.SMA(df_klines['closed_price'].values, timeperiod=200)
        ma50 = ta.SMA(df_klines['closed_price'].values, timeperiod=50)
        ma20 = ta.SMA(df_klines['closed_price'].values, timeperiod=20)
        ema20 = ta.EMA(df_klines['closed_price'].values, timeperiod=20)
        slowk, slowd = ta.STOCH(df_klines['higest_price'].values, df_klines['lowest_price'].values, df_klines['closed_price'].values, fastk_period=5, slowk_period=3, slowk_matype=0, slowd_period=3, slowd_matype=0)
        macd, macdsignal, macdhist = ta.MACD(df_klines['closed_price'].values, fastperiod=12, slowperiod=26, signalperiod=9)

        operation = op(self.symbol)
        print(f'Balance inicial: {self.bac_account}')
        
        for i in df_klines.index:
            date = datetime.datetime.fromtimestamp(df_klines[0][i]/1000)
            '''feed_4h = fd(self.symbol, '30m', 500)
            feed_4h.start_date = date-datetime.timedelta(days=3)
            feed_4h.start_date = int(feed_4h.start_date.timestamp()*1000)            
            feed_4h.end_date = df_klines[0][i]
            feed_4h.end_date= df_klines[0][i]
            klines_4h = feed_4h.get_df_klines_interval()
            tendencia = self.get_tendencia(klines_4h)'''
            #if tendencia == 'Ascendente':

            if ma20[i] > ma200[i] and macd[i] < 0 and macdsignal[i] < 0 and macd[i] > macdsignal[i] and not operation.status:
                self.bac_account = operation.buy(self.bac_account.account_balance, df_klines['closed_price'][i], self.bac_account)
                print(f'{date} - {df_klines[4][i]} - {ma50[i]} - {ma200[i]}')
                print(self.bac_account)

            elif df_klines['closed_price'][i] >= operation.buyPrice and df_klines['closed_price'][i] >= operation.buyPrice + (operation.buyPrice * 0.005) and operation.status:
                self.bac_account = operation.sell(operation.get_operation_balance(), df_klines['closed_price'][i], self.bac_account)
                self.current_balance = self.bac_account.account_balance
                print(f'{date} - {df_klines[4][i]} - {ma50[i]} - {ma200[i]}')
                cnt_operations += 1
                win_rate += 1
                print(f'Win operation')

            elif df_klines['closed_price'][i] <= operation.buyPrice and df_klines['lowest_price'][i] <= operation.buyPrice - (operation.buyPrice*0.003) and operation.status:
                self.bac_account = operation.sell(operation.get_operation_balance(), df_klines['closed_price'][i], self.bac_account)
                self.current_balance = self.bac_account.account_balance
                print(f'{date} - {df_klines[4][i]} - {stdup[i]} - {mean[i]} - {stddown[i]}')
                cnt_operations += 1
                loss_rate += 1
                print(f"Loss Operation: {df_klines['closed_price'][i] }")
            
            
            self.last_price = df_klines['closed_price'][i]

            #else:
            #    pass

        print(f'Cantidad de operaciones: {cnt_operations}')
        print(f'Cantidad de operaciones ganadas: {win_rate}')
        print(f'Cantidad de operaciones perdidas: {loss_rate}')
        print(f'Balance despues de ultima venta: {self.current_balance}')
        print(f'Balance actual de crypto: {operation.get_operation_balance()}')
        if self.bac_account.account_balance > 0:
            print(f'Balance actual de BUSD: {self.bac_account.account_balance}')
        else:
            print(f'Balance actual de BUSD: {operation.get_operation_balance()*self.last_price}')

    def get_tendencia(self, df_klines):
        df_klines['closed_price'] = df_klines.apply(lambda x: float(x[4]) ,axis=1)
        sma = ta.SMA(df_klines['closed_price'].values, timeperiod=20)
        sma_actual = sma[len(sma)-1]
        sma_anterior = sma[len(sma)-2]
        if sma_actual > sma_anterior:
            return 'Ascendente'
        else:
            return 'Descendente'

    def buyLong(self, buyQty, buyPrice, stopPrice):
        buyOrder = self.client.create_order(
                symbol=self.symbol,
                side='BUY',
                type='STOP_LOSS_LIMIT',
                quantity=buyQty,
                price='{:.8f}'.format(round(buyPrice)),
                stopPrice='{:.8f}'.format(round(stopPrice)),
                timeInForce='GTC')
        return buyOrder

    def sellShort(self, sellQty, sellPrice, stopPrice):
        sellOrder = self.client.create_order(
                symbol=self.symbol,
                side='SELL',
                type='STOP_LOSS_LIMIT',
                quantity=sellQty,
                price='{:.8f}'.format(round(sellPrice)),
                stopPrice='{:.8f}'.format(round(stopPrice)),
                timeInForce='GTC')
        return sellOrder

    def run():
        pass


if __name__ == "__main__":
    symbol = 'BTCBUSD'
    interval = '5m'
    limit = 1000
    feed = fd(symbol=symbol, interval=interval, limit=limit)
    #feed.start_date = datetime.datetime.now() - datetime.timedelta(days=60)
    #feed.start_date = int(feed.start_date.timestamp()*1000)
    #feed.end_date = datetime.datetime.now() - datetime.timedelta(days=1)
    #feed.end_date = int(feed.end_date.timestamp()*1000)
    st = Strategy(symbol, feed.get_Client(), feed.get_df_binance_klines())
    st.backtestBB(20, 2, 0)



