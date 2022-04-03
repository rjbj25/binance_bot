import pandas as pd

'''
    This class abstract the operations of the trading strategy.
'''

class Operation:
    def __init__(self, symbol):
        self.__symbol = symbol
        self.status = False
        self.__op_balance = 0
        self.buyPrice = 0
        self.stop_price = None


    def buy(self, buyQty, buyPrice, bac_account):
        self.buyPrice = buyPrice
        
        commision = buyQty * 0.001
        self.__op_balance = (buyQty - commision) / buyPrice
        print(f'A Buy operation has been executed of {self.__symbol} at {buyPrice}')
        self.status = True
        bac_account.account_balance = bac_account.account_balance - buyQty
        return bac_account

    def close_operation(self, currentPrice):
        self.__op_balance = 0

    def sell(self, sellQty, sellPrice, bac_account):
        commision = sellQty * 0.001
        account_balance = sellQty * sellPrice
        self.status = False
        bac_account.account_balance = bac_account.account_balance + account_balance - commision
        print(f'A Sell operation has been executed, new balance: {bac_account.account_balance}')
        self.__op_balance = 0
        return bac_account

    def get_operation_balance(self):
        return self.__op_balance
        

        
        