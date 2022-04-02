

class BacktestAccount:
    def __init__(self, account_balance, account_currency):
        self.account_balance = account_balance
        self.account_currency = account_currency

    def __str__(self):
        return f'Account Balance: {self.account_balance}, Account Currency: {self.account_currency}'