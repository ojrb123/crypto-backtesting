import pandas as pd

class Backtester:
    def __init__(self, data):
        self.data = data
        self.positions = pd.Series(index=self.data.index, dtype=int)
        self.portfolio = pd.DataFrame(index=self.data.index)
        self.start_balance = 100000  # Initial balance in USD
        self.balance = self.start_balance
        self.unit_size = 100  # Number of shares per trade

    def execute_strategy(self):
        for i in range(1, len(self.data)):
            # Implement your trading strategy here
            if self.data['Close'][i] > self.data['Close'][i - 1]:
                self.buy(i)
            elif self.data['Close'][i] < self.data['Close'][i - 1]:
                self.sell(i)

    def buy(self, i):
        units_to_buy = int(self.balance / self.data['Close'][i] / self.unit_size)
        self.positions.iloc[i] = units_to_buy * self.unit_size
        self.balance -= units_to_buy * self.data['Close'][i]

    def sell(self, i):
        units_to_sell = self.positions.iloc[i - 1]
        self.positions.iloc[i] = -units_to_sell
        self.balance += units_to_sell * self.data['Close'][i]

    def calculate_portfolio_value(self):
        self.portfolio['Cash'] = self.balance + (self.positions * self.data['Close'])
        self.portfolio['Total'] = self.portfolio['Cash'] + self.balance

    def run_backtest(self):
        self.execute_strategy()
        self.calculate_portfolio_value()


price_data = pd.DataFrame({
    'Close': [100, 105, 95, 110, 120, 115, 105, 100, 110, 115],
}, index=pd.date_range('2022-01-01', periods=10))

# Create a backtester instance and run the backtest
backtester = Backtester(price_data)
backtester.run_backtest()

# View the resulting portfolio
print(backtester.portfolio)