from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import backtrader as bt


import datetime
import os.path
import sys

class HMA_PSAR_Strategy(bt.Strategy):
    params = (('hma_period', 7), ('psar_af', 0.02), ('psar_afmax', 0.2), ('percent_target', 3))

    def __init__(self):
        self.hma = bt.indicators.HullMovingAverage(self.datas[0])
        self.psar = bt.indicators.ParabolicSAR(self.datas[0])
        self.order = None
        self.entry_price = None
        self.signal_count = 0
        self.success_count = 0
        self.dataclose = self.datas[0].close

    def next(self):
        if self.order:  # Check if an order is pending, if so, do nothing
            return

        if not self.position:  # Not in the market
            if self.hma[0] < self.dataclose[0] and self.psar[0] < self.dataclose[0]:
                self.order = self.buy()
                self.entry_price = self.data.close[0]
                self.signal_count += 1
            elif self.hma[0] > self.dataclose[0] and self.psar[0] > self.dataclose[0]:
                self.order = self.sell()
                self.entry_price = self.dataclose[0]
                self.signal_count += 1
        else:
            # Check for target profit
            if self.position.size > 0:  # In a long position
                if self.dataclose[0] >= self.entry_price[0] * (1 + self.params.percent_target / 100):
                    self.order = self.sell()
                    self.success_count += 1
            elif self.position.size < 0:  # In a short position
                if self.dataclose[0] <= self.entry_price * (1 - self.params.percent_target / 100):
                    self.order = self.close()
                    self.success_count += 1

    def stop(self):
        if self.signal_count > 0:
            probability = (self.success_count / self.signal_count) * 100
            print(f'Probability of achieving 5% price move: {probability:.2f}%')

# Add the strategy to Cerebro, load data and run the backtest


if __name__ == '__main__':
    # Create a cerebro entity
    cerebro = bt.Cerebro()

    # Add a strategy
    cerebro.addstrategy(HMA_PSAR_Strategy)

    datapath = 'data/LINK-USDT15.csv'

    # Create a Data Feed
    data = bt.feeds.GenericCSVData(
        dataname=datapath,
        fromdate=datetime.datetime(2023, 10, 2),
        todate=datetime.datetime(2024, 1, 31),
        open = 1,
        high = 2,
        low = 3,
        close = 4,
        volume = -1,
        openinterest = -1,
        dtformat='%Y-%m-%dT%H:%M:%SZ',  # Specify the correct date format
        datetime=0,  # Index of the column containing datetime information
    )

    cerebro.adddata(data)

    cerebro.addsizer(bt.sizers.FixedSize, stake=1)

    cerebro.broker.setcash(100000)

    cerebro.broker.setcommission(commission=0.001)

    # Print out the starting conditions
    print('Starting Portfolio Value: %.2f' % cerebro.broker.getvalue())

    # Run over everything
    cerebro.run()

    print('Ending Portfolio Value: %.2f' % cerebro.broker.getvalue())

    cerebro.plot(volume = False)