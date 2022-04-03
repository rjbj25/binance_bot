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
        df_klines = pd.DataFrame(self.klines)
        df_klines['closed_price'] = df_klines.apply(lambda x: float(x[4]) ,axis=1)
        df_klines['lowest_price'] = df_klines.apply(lambda x: float(x[3]) ,axis=1)
        stdup, mean, stddown = ta.BBANDS(df_klines['closed_price'].values, timeperiod=timeperiod, nbdevup=nbdevup, nbdevdn=nbdevdn, matype=0)
        rsi = ta.RSI(df_klines['closed_price'].values, timeperiod=timeperiod)
        
        operation = op(self.symbol)
        print(f'Balance inicial: {self.bac_account}')
        feed_4h = fd(self.symbol, '4h', 500)
        klines_4h = feed_4h.get_df_klines()
        tendencia = self.get_tendencia(klines_4h)

        if tendencia == 'Ascendente':
            for i in df_klines.index:
                date = datetime.datetime.fromtimestamp(df_klines[0][i]/1000).strftime("%Y-%m-%d %H:%M:%S")

                if df_klines['closed_price'][i] <= stddown[i] + (stddown[i] * 0.001) and not operation.status and self.bac_account.account_balance > 0:
                    self.bac_account = operation.buy(self.bac_account.account_balance, df_klines['closed_price'][i], self.bac_account)
                    print(f'{date} - {df_klines[4][i]} - {stdup[i]} - {mean[i]} - {stddown[i]}')
                    print(self.bac_account)

                elif df_klines['closed_price'][i] >= operation.buyPrice and df_klines['closed_price'][i] >= stdup[i] and operation.status:
                    self.bac_account = operation.sell(operation.get_operation_balance(), df_klines['closed_price'][i], self.bac_account)
                    self.current_balance = self.bac_account.account_balance
                    print(f'{date} - {df_klines[4][i]} - {stdup[i]} - {mean[i]} - {stddown[i]}')
                    cnt_operations += 1
                    win_rate += 1
                    print(f"Win Operation: {df_klines['closed_price'][i] }")

                elif df_klines['closed_price'][i] <= operation.buyPrice and df_klines['lowest_price'][i] <= stddown[i] - (stddown[i]*0.001) and operation.status:
                    self.bac_account = operation.sell(operation.get_operation_balance(), df_klines['closed_price'][i], self.bac_account)
                    self.current_balance = self.bac_account.account_balance
                    print(f'{date} - {df_klines[4][i]} - {stdup[i]} - {mean[i]} - {stddown[i]}')
                    cnt_operations += 1
                    loss_rate += 1
                    print(f"Loss Operation: {df_klines['closed_price'][i] }")
            

        print(f'Cantidad de operaciones: {cnt_operations}')
        print(f'Cantidad de operaciones ganadas: {win_rate}')
        print(f'Cantidad de operaciones perdidas: {loss_rate}')
        print(f'Balance despues de ultima venta: {self.current_balance}')
        print(f'Balance actual de crypto: {operation.get_operation_balance()}')
        if self.bac_account.account_balance > 0:
            print(f'Balance actual de BUSD: {self.bac_account.account_balance}')
        else:
            print(f'Balance actual de BUSD: {operation.get_operation_balance()*self.last_price}')
        print(f'{self.bac_account}')

    def get_tendencia(df_klines):
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
    st = Strategy('BTCBUSD', feed.get_Client(), feed.get_df_klines())
    st.backtestBB(20, 2, 0)



