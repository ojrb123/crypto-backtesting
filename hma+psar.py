from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import datetime

import backtrader as bt

# Create a Strategy
class TestStrategy(bt.Strategy):

    params = (('hma_period', 7), ('psar_af', 0.02), ('psar_afmax', 0.2), ('percent_target', 3))

    def log(self, txt, dt=None):
        ''' Logging function for this strategy'''
        dt = dt or self.datas[0].datetime.date(0)
        print('%s, %s' % (dt.isoformat(), txt))

    def __init__(self):
        # Keep a reference to the "close" line in the data[0] dataseries
        self.dataclose = self.datas[0].close

        self.order = None
        self.buyprice = None
        self.comm = None
        self.hma = bt.indicators.HullMovingAverage(self.data.close, period=self.params.hma_period)
        self.psar = bt.indicators.ParabolicSAR(af=self.params.psar_af, afmax=self.params.psar_afmax)
        self.bs = bt.indicators.

    def notify_order(self, order):
        if order.status in [order.Submitted, order.Accepted]:
            # Buy/Sell order submitted/accepted to/by broker - Nothing to do
            return

        # Check if an order has been completed
        # Attention: broker could reject order if not enough cash
        if order.status in [order.Completed]:
            if order.isbuy():
                self.log(
                    'BUY EXECUTED, Price: %.2f, Cost: %.2f, Comm %.2f' %
                    (order.executed.price,
                     order.executed.value,
                     order.executed.comm))

                self.buyprice = order.executed.price
                self.buycomm = order.executed.comm
            else:  # Sell
                self.log('SELL EXECUTED, Price: %.2f, Cost: %.2f, Comm %.2f' %
                         (order.executed.price,
                          order.executed.value,
                          order.executed.comm))

            self.bar_executed = len(self)

        elif order.status in [order.Canceled, order.Margin, order.Rejected]:
            self.log('Order Canceled/Margin/Rejected')

        self.order = None

    def notify_trade(self, trade):
        if not trade.isclosed:
            return

        self.log('OPERATION PROFIT, GROSS %.2f, NET %.2f' %
                 (trade.pnl, trade.pnlcomm))

    def next(self):
        self.log('Close, %.2f' % self.dataclose[0])

        # Check if we are in a position
        if self.order:
            return
        
        if self.position:
            if (int(self.buyprice * 1.05)) <= (int(self.dataclose[0])):
                self.log('SELL CREATE 10, %.2f, %.2f' % (self.dataclose[0], self.buyprice))
                self.log('calc, %.2f' % int(self.buyprice * 1.05))
                self.order = self.sell()

            elif (int(self.buyprice * 0.98)) >= (int(self.dataclose[0])):
                self.log('SL CREATE 2, %.2f, %.2f' % (self.dataclose[0], self.buyprice))
                self.order = self.sell() 
            
        elif not self.position:
            if self.dataclose[0] == 65 :
                self.log('BUY CREATE, %.2f' % self.dataclose[0])

                self.order = self.buy()



if __name__ == '__main__':
    # Create a cerebro entity
    cerebro = bt.Cerebro()

    # Add a strategy
    cerebro.addstrategy(TestStrategy)

    datapath = 'data/LINK-USDT15-SMALL.csv'

    # Create a Data Feed
    data = bt.feeds.GenericCSVData(
        dataname=datapath,
        fromdate=datetime.datetime(2022, 1, 13),
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

    cerebro.broker.setcash(100)

    cerebro.broker.setcommission(commission=0.001)

    # Print out the starting conditions
    print('Starting Portfolio Value: %.2f' % cerebro.broker.getvalue())

    # Run over everything
    cerebro.run()

    cerebro.plot(volume = False)

    print('Ending Portfolio Value: %.2f' % cerebro.broker.getvalue())

    # Print out the final result
