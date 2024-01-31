import backtrader as bt
import datetime

# Custom Data Feed Class for TradingView CSV Data
class TradingViewCSVData(bt.feeds.GenericCSVData):
    params = (
        ('dtformat', '%Y-%m-%dT%H:%M:%SZ'),  # ISO datetime format including 'Z' for UTC
        ('datetime', 0),  # Position of the datetime field in the CSV
        ('time', -1),     # No separate time field here, it's included in the datetime
        ('open', 1),      # Position for Open price in the CSV
        ('high', 2),      # Position for High price in the CSV
        ('low', 3),       # Position for Low price in the CSV
        ('close', 4),     # Position for Close price in the CSV
        ('volume', -1),   # No volume in the CSV
        ('openinterest', -1),  # No open interest in the CSV
    )