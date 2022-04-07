from tabnanny import check
from feed import Feed as fd
from operation import Operation as op
from account import BacktestAccount as bac
import talib as ta
import pandas as pd
import datetime

'''This class implement a RSI trading strategy.'''

class Strategy:

    def __init__(self, symbol, client, klines, capital):
        self.symbol = symbol
        self.client = client
        self.klines = klines
        self.bac_account = bac(capital, 'BUSD')
        self.balance_inicial = self.bac_account.account_balance
        self.current_balance = 0
        self.last_price = 0
        self.current_price = 0
        
    def backtestInfinitGrid(self,percent,grid):
        operation = op(self.symbol)
        df_klines = pd.DataFrame(self.klines)
        df_klines['closed_price'] = df_klines.apply(lambda x: float(x[4]) ,axis=1)
        df_klines['lowest_price'] = df_klines.apply(lambda x: float(x[3]) ,axis=1)
        df_klines['higest_price'] = df_klines.apply(lambda x: float(x[2]) ,axis=1)
        buy_operation = 0
        sell_operation = 0
        qtysold = 0


        for i in df_klines.index:
            date = datetime.datetime.fromtimestamp(df_klines[0][i]/1000)
            sell_qty = self.check_operation_list(operation.operation_list, operation.operation_amount_list, df_klines['closed_price'][i])
            #print(sell_qty)
            if i == 0:
                print(f'Last price: {self.last_price}')
                buyQty = self.bac_account.account_balance * percent
                self.bac_account = operation.buy(buyQty, df_klines['closed_price'][i], self.bac_account)
                self.last_price = df_klines['closed_price'][i]
                self.bac_account.account_balance_crypto = operation.get_operation_balance() + self.bac_account.account_balance_crypto
                buy_operation += 1
                operation.operation_list.append(df_klines['closed_price'][i])
                operation.operation_amount_list.append(operation.get_operation_balance())
                print(f"Fecha: {date} - Precio de cierre: {df_klines['closed_price'][i]} - Balance de cuenta: {self.bac_account.account_balance} - Operacion: Primera compra - Ultima operacion: {self.last_price} - Cantidad vendida en BUSD: {buyQty}")
                print(f'Cantidad disponible en crypto: {self.bac_account.account_balance_crypto}')
            elif df_klines['closed_price'][i] < self.last_price - (self.last_price * grid) and self.bac_account.account_balance > 10:
                print(f'Last price: {self.last_price}')
                buyQty = self.bac_account.account_balance * percent
                self.bac_account = operation.buy(buyQty, df_klines['closed_price'][i], self.bac_account)
                self.last_price = df_klines['closed_price'][i]
                self.bac_account.account_balance_crypto = operation.get_operation_balance() + self.bac_account.account_balance_crypto
                buy_operation += 1
                print(f"Fecha: {date} - Precio de cierre: {df_klines['closed_price'][i]} - Balance de cuenta: {self.bac_account.account_balance} - Ultima operacion: {self.last_price} - Cantidad vendida en BUSD: {buyQty}")
                print(f'Cantidad disponible en crypto: {self.bac_account.account_balance_crypto}')
            elif self.bac_account.account_balance_crypto > 0 and df_klines['closed_price'][i] > self.last_price + (self.last_price * grid) and sell_qty is not None and len(sell_qty) > 0:
                print(f'Cantidad a vender en CRYPTO: {sell_qty[0]}')
                self.bac_account = operation.sell(sell_qty[0], df_klines['closed_price'][i], self.bac_account)
                self.bac_account.account_balance_crypto = self.bac_account.account_balance_crypto - sell_qty[0]
                sell_operation += 1
                operation.operation_list.pop(sell_qty[2])
                operation.operation_amount_list.pop(sell_qty[2])
                print(f"Fecha: {date} - Precio de cierre: {df_klines['closed_price'][i]} - Balance de cuenta: {self.bac_account.account_balance} - Balance crypto: {self.bac_account.account_balance_crypto} - Operacion: Venta - Ultima operacion: {self.last_price}")
                print(f'Cantidad disponible en crypto: {self.bac_account.account_balance_crypto}')
            elif self.bac_account.account_balance < 10:
                print(f"Sin fondos para realizar operaciones")

            

            self.current_price = df_klines['closed_price'][i]
        print(f"Fecha: {date} - Balance de cuenta: {self.bac_account.account_balance} - Balance de cuenta en crypto: {self.bac_account.account_balance_crypto} - Valor de crypto en BUSD {self.bac_account.account_balance_crypto * self.current_price}")
        print(f"Balance total actual {self.bac_account.account_balance + self.bac_account.account_balance_crypto * self.current_price}")
        print(f"Operaciones de compra: {buy_operation} - Operaciones de venta: {sell_operation}")
        return self.bac_account.account_balance + self.bac_account.account_balance_crypto * self.current_price


    def check_operation_list(self, operation_list, operation_amount_list, current_price):
        for i in range(len(operation_list)):
            if current_price > operation_list[i]:
                return [operation_amount_list[i], operation_list[i], i]

    def backtestBB(self, timeperiod, nbdevup, nbdevdn):
        cnt_operations = 0
        win_rate = 0
        loss_rate = 0
        tendencia = None
        df_klines = pd.DataFrame(self.klines)
        df_klines['closed_price'] = df_klines.apply(lambda x: float(x[4]) ,axis=1)
        df_klines['lowest_price'] = df_klines.apply(lambda x: float(x[3]) ,axis=1)
        df_klines['higest_price'] = df_klines.apply(lambda x: float(x[2]) ,axis=1)

        #Indicadores
        stdup, mean, stddown = ta.BBANDS(df_klines['closed_price'].values, timeperiod=timeperiod, nbdevup=nbdevup, nbdevdn=nbdevdn, matype=0)
        rsi = ta.RSI(df_klines['closed_price'].values, timeperiod=timeperiod)
        ma100 = ta.SMA(df_klines['closed_price'].values, timeperiod=100)
        ma200 = ta.SMA(df_klines['closed_price'].values, timeperiod=200)
        ma50 = ta.SMA(df_klines['closed_price'].values, timeperiod=50)
        ma20 = ta.SMA(df_klines['closed_price'].values, timeperiod=20)
        ema20 = ta.EMA(df_klines['closed_price'].values, timeperiod=20)
        adx = ta.ADX(df_klines['higest_price'].values, df_klines['lowest_price'].values, df_klines['closed_price'].values, timeperiod=14)
        slowk, slowd = ta.STOCH(df_klines['higest_price'].values, df_klines['lowest_price'].values, df_klines['closed_price'].values, fastk_period=5, slowk_period=3, slowk_matype=0, slowd_period=3, slowd_matype=0)
        macd, macdsignal, macdhist = ta.MACD(df_klines['closed_price'].values, fastperiod=12, slowperiod=26, signalperiod=9)

        operation = op(self.symbol)
        print(f'Balance inicial: {self.bac_account}')

        #Backtesting
        for i in df_klines.index:
            date = datetime.datetime.fromtimestamp(df_klines[0][i]/1000)
            #if tendencia == 'Ascendente':
            if i > 3:

                if  not operation.status and self.crossover(macd,macdsignal,i) and adx[i] > adx[i-1] and adx[i-1] > adx[i-2]:
                    self.bac_account = operation.buy(self.bac_account.account_balance, df_klines['closed_price'][i], self.bac_account)
                    print(f'{date} - {df_klines[4][i]} - {ma50[i]} - {ma200[i]}')
                    print(self.bac_account)

                elif df_klines['closed_price'][i] > operation.buyPrice * (operation.buyPrice * 0.008) and operation.status:
                    self.bac_account = operation.sell(operation.get_operation_balance(), df_klines['closed_price'][i], self.bac_account)
                    self.current_balance = self.bac_account.account_balance
                    print(f'{date} - {df_klines[4][i]} - {ma50[i]} - {ma200[i]}')
                    cnt_operations += 1
                    if operation.buyPrice > df_klines['closed_price'][i]:
                        print(f"Loss Operation at: {df_klines['closed_price'][i]}")
                        loss_rate += 1
                    else:
                        print(f"Win Operation at: {df_klines['closed_price'][i]}")
                        win_rate += 1
                    
                '''
                elif df_klines['closed_price'][i] <= operation.buyPrice and df_klines['lowest_price'][i] <= operation.buyPrice - (operation.buyPrice*0.003) and operation.status:
                    self.bac_account = operation.sell(operation.get_operation_balance(), df_klines['closed_price'][i], self.bac_account)
                    self.current_balance = self.bac_account.account_balance
                    print(f'{date} - {df_klines[4][i]} - {stdup[i]} - {mean[i]} - {stddown[i]}')
                    cnt_operations += 1
                    loss_rate += 1
                    print(f"Loss Operation: {df_klines['closed_price'][i] }")
                '''
            
            self.last_price = df_klines['closed_price'][i]


        print(f'Cantidad de operaciones: {cnt_operations}')
        print(f'Cantidad de operaciones ganadas: {win_rate}')
        print(f'Cantidad de operaciones perdidas: {loss_rate}')
        print(f'Balance despues de ultima venta: {self.current_balance}')
        print(f'Balance actual de crypto: {operation.get_operation_balance()}')
        if self.bac_account.account_balance > 0:
            print(f'Balance actual de BUSD: {self.bac_account.account_balance}')
            return self.bac_account.account_balance
        else:
            print(f'Balance actual de BUSD: {operation.get_operation_balance()*self.last_price}')
            return operation.get_operation_balance()*self.last_price

    def crossover(self, serie1, serie2, index):
        if serie1[index-1] < serie2[index-1] and serie1[index]>serie2[index]:
            return True
        else:
            return False

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
    capital = 1000    
    for i in range(10):
        feed = fd(symbol=symbol, interval=interval, limit=limit)
        feed.start_date = datetime.datetime.now() - datetime.timedelta(days=30-i*3)
        #feed.start_date = datetime.datetime.now() - datetime.timedelta(days=3)
        feed.start_date = int(feed.start_date.timestamp()*1000)
        feed.end_date = datetime.datetime.now() - datetime.timedelta(days=0)
        feed.end_date = int(feed.end_date.timestamp()*1000)
        st = Strategy(symbol, feed.get_Client(), feed.get_df_binance_klines_interval(), capital)
        #capital = st.backtestBB(20, 2, 0)
        capital = st.backtestInfinitGrid(percent=0.05,grid=0.005)
    



