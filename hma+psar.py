from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import datetime
import os.path
import sys

import backtrader as bt

# Create a Strategy
class TestStrategy(bt.Strategy):

    def log(self, txt, dt=None):
        ''' Logging function for this strategy'''
        dt = dt or self.datas[0].datetime.date(0)
        print('%s, %s' % (dt.isoformat(), txt))

    def __init__(self):
        # Keep a reference to the "close" line in the data[0] dataseries
        self.dataclose = self.datas[0].close
        self.price_history = []

        # Add Parabolic SAR indicator
        self.sar = bt.indicators.ParabolicSAR(self.datas[0])

        # Initialize prev_sar and buy_price
        self.prev_sar = None
        self.buy_price = None

    def notify_order(self, order):
        if order.status in [order.Submitted, order.Accepted]:
            # Buy/Sell order submitted/accepted to/by broker - Nothing to do
            return

        # Check if an order has been completed
        if order.status in [order.Completed]:
            if order.isbuy():
                self.buy_price = order.executed.price
                self.log(
                    'BUY EXECUTED, Price: %.2f, Cost: %.2f, Comm %.2f' %
                    (order.executed.price,
                     order.executed.value,
                     order.executed.comm))

            elif order.issell():
                self.log('SELL EXECUTED, Price: %.2f, Cost: %.2f, Comm %.2f' %
                         (order.executed.price,
                          order.executed.value,
                          order.executed.comm))

            self.bar_executed = len(self)

        elif order.status in [order.Canceled, order.Margin, order.Rejected]:
            self.log('Order Canceled/Margin/Rejected')

        self.order = None

    def next(self):
        self.log('Close, %.2f' % self.dataclose[0])

        # Check if we are in a position
        if self.position:
            if self.dataclose[0] <= self.buy_price * 0.98:
                self.log('SELL CREATE (Price dropped below 98%% of buy price), %.2f' % self.dataclose[0])
                self.order = self.close()
            
            elif self.dataclose[0] >= self.buy_price * 1.05:
                self.log('SELL CREATE (Price increased aboe 15%% of buy price), %.2f' % self.dataclose[0])
                self.order = self.close()

            return

        # Update the price history
        if self.dataclose[0] > self.sar[0] and not self.position:
            self.log('BUY CREATE, %.2f' % self.dataclose[0])
            self.order = self.buy()


if __name__ == '__main__':
    # Create a cerebro entity
    cerebro = bt.Cerebro()

    # Add a strategy
    cerebro.addstrategy(TestStrategy)

    datapath = 'data/LTC-USDT15.csv'

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

    # Print out the final result
