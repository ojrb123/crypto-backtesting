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

        # Add Bollinger Bands indicator
        self.bollinger = bt.indicators.BollingerBands(self.datas[0], period=21, devfactor=2)

        # Initialize buy_price
        self.buy_price = None

        # Set parameters for trailing stop and take profit
        self.trailing_stop_percent = 4
        self.take_profit_percent = 15

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

                # Set trailing stop and take profit for the buy order
                self.sell(
                    exectype=bt.Order.StopTrail,
                    trailpercent=self.trailing_stop_percent,
                    parent=order
                )

                self.sell(
                    exectype=bt.Order.Limit,
                    price=order.executed.price * (1 + self.take_profit_percent / 100),
                    parent=order
                )

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
            # Check if the close price is below the lower Bollinger Band for selling
            if self.dataclose[0] < self.bollinger.lines.bot:
                self.log('SELL CREATE (Close below Bollinger Bands), %.2f' % self.dataclose[0])
                self.order = self.close()

            return

        # Check if close is greater than or equal to the lower Bollinger Band
        if self.dataclose[0] >= self.bollinger.lines.bot:
            # Check if the previous close is less than the lower Bollinger Band
            if self.dataclose[-1] < self.bollinger.lines.bot[-1]:
                self.log('BUY CREATE, %.2f' % self.dataclose[0])
                self.order = self.buy(size=40)

        # Update the price history
        self.price_history.append(self.dataclose[0])

        # Remove the oldest price to keep the history size fixed
        if len(self.price_history) > 21:
            self.price_history.pop(0)


if __name__ == '__main__':
    # Create a cerebro entity
    cerebro = bt.Cerebro()

    # Add a strategy
    cerebro.addstrategy(TestStrategy)

    datapath = 'data/LTC-USDT15.csv'

    # Create a Data Feed
    data = bt.feeds.GenericCSVData(
        dataname=datapath,
        fromdate=datetime.datetime(2023, 10, 13),
        todate=datetime.datetime(2024, 1, 31),
        open=1,
        high=2,
        low=3,
        close=4,
        volume=-1,
        openinterest=-1,
        dtformat='%Y-%m-%dT%H:%M:%SZ',  # Specify the correct date format
        datetime=0,  # Index of the column containing datetime information
    )

    cerebro.adddata(data)

    cerebro.addsizer(bt.sizers.FixedSize, stake=40)

    cerebro.broker.setcash(100000)

    cerebro.broker.setcommission(commission=0.001)

    # Print out the starting conditions
    print('Starting Portfolio Value: %.2f' % cerebro.broker.getvalue())

    # Run over everything
    cerebro.run()

    cerebro.plot(volume=False)

    # Print out the final result
