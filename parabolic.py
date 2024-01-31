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
            # Check if SAR is above Close and above previous SAR for selling
            if self.sar[0] > self.dataclose[0] and self.sar[0] > self.prev_sar:
                self.log('SELL CREATE (SAR above Close and above previous SAR), %.2f' % self.dataclose[0])
                self.order = self.close()
            elif self.dataclose[0] <= self.buy_price * 0.9:
                self.log('SELL CREATE (Price dropped below 90%% of buy price), %.2f' % self.dataclose[0])
                self.order = self.close()

            return

        # Update the price history
        self.price_history.append(self.dataclose[0])

        # Check if we have enough data for the past 14 days
        if len(self.price_history) == 14:
            # Calculate the percentage drop over the past 14 days
            max_price = max(self.price_history)
            min_price = min(self.price_history)
            percentage_drop = ((max_price - min_price) / max_price) * 100

            # Check if there has been a 30% drop
            if percentage_drop >= 30:
                self.log('BUY CREATE, %.2f' % self.dataclose[0])
                self.order = self.buy(size = 4000)

            # Check if SAR is below Close after a sell
            elif self.prev_sar is not None and self.sar[0] < self.dataclose[0] and self.prev_sar > self.dataclose[0]:
                self.log('BUY CREATE (SAR below Close after a sell), %.2f' % self.dataclose[0])
                self.order = self.buy(size=self.broker.cash)

            # Update the previous SAR value
            self.prev_sar = self.sar[0]

            # Remove the oldest price to keep the history size fixed
            self.price_history.pop(0)


if __name__ == '__main__':
    # Create a cerebro entity
    cerebro = bt.Cerebro()

    # Add a strategy
    cerebro.addstrategy(TestStrategy)

    datapath = 'AVAX-USD5.csv'

    # Create a Data Feed
    data = bt.feeds.YahooFinanceCSVData(
        dataname=datapath,
        fromdate=datetime.datetime(2019, 1, 30),
        todate=datetime.datetime(2021, 11, 30),
        reverse=False)

    cerebro.adddata(data)

    cerebro.addsizer(bt.sizers.FixedSize, stake=2)

    cerebro.broker.setcash(100000)

    cerebro.broker.setcommission(commission=0.001)

    # Print out the starting conditions
    print('Starting Portfolio Value: %.2f' % cerebro.broker.getvalue())

    # Run over everything
    cerebro.run()

    cerebro.plot()

    # Print out the final result
   
