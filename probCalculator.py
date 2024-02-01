import pandas as pd 
import ta_py as ta;
import csv

df = './data/LTC-USDT15.csv'

class DataFeed:

    def __init__(self, data):

        self.data = data
        self.datetime = data[0]
        self.open = data[1]
        self.high = data[2]
        self.low = data[3] 
        self.close = data[4]


    def opendata(self):
        with open(self.data, 'r') as csv_file:
            reader = csv.reader(csv_file)
            return reader


    # Returns a datasets HMA
    # data -- An array of candle close prices [close, close]
    # length -- The window size to use in the calculation
    def HMA(data, length):

        return ta.hull(data, length)

    # Returns a datasets PSAR
    # data -- An array of arrays where the sub arrays contain the [[high, low]]
    # step -- default to 0.02
    # max -- default to 0.2
    def PSAR(data, step=0.02, max=0.2):

        return ta.psar(data, step, max)
    
    # Returns a datasets supertrend value
    # data -- An array of arrays where the sub arrays contain the [[high, close, low]]
    def SuperTrend(data, length=3, multiplier=0.5):

        return ta.supertrend(data, length, multiplier)
    


# get PSAR array of values
def PSAR(data, step=0.02, max=0.2):

    return ta.psar(data, step, max)

# get the required data for PSAR calculation
def get_PSAR_Data(data, psar_data=[]):
    with open(data, 'r') as csv_psar:
        reader = csv.reader(csv_psar)
        next(reader)
        for row in reader:
            psar_data.append([float(row[2]), float(row[3])])
        return psar_data

# return true if close is greater than psar
# used for checking for cross
def PSAR_position(psar_value, close):
    return float(close) > psar_value

# def initial_PSAR(data)

# return hma value
def HMA(data, length):

    return ta.hull(data, length)

# returns true if close is greater than hma
# used for checking for a cross
def HMA_position(hma_value, close):
    return float(close) > hma_value[0]

#calculate the initial hma
def initial_hma(data, length):
    with open(data, 'r') as csv_file:
        reader = csv.reader(csv_file)
        next(reader)  # Skip header
        initial_data = [float(row[4]) for _, row in zip(range(length), reader)]
        initial_hma_val = HMA(initial_data, length-2)
    return initial_hma_val, initial_data[-1]  # Return last close price too

with open(df, 'r') as csv_file:
    reader = csv.reader(csv_file)
    next(reader)
    HMA_holder = []
    PSAR_data = get_PSAR_Data(df)
    PSAR_holder = PSAR(PSAR_data)
    WINDOW = 0 
    TRIALS = 0
    CANDLES = 0
    BUY = False
    BUY_PRICE = 0.00
    WIN = 0
    # prev_hma_state = True
    prev_psar_state = True
    initial_hma_val, last_close_for_hma = initial_hma(df, 9)

    # Set prev_hma_state based on the comparison
    prev_hma_state = last_close_for_hma > initial_hma_val[0]  # Assuming HMA function returns a list or similar
    for _ in range(8): 
        next(reader)

    for row in reader:
        HMA_holder.append(row[4])
        print(HMA_holder)
        WINDOW += 1
        CANDLES += 1
        if WINDOW == 11:
            HMA_val = HMA(HMA_holder, WINDOW-2)
            curr_hma_state = HMA_position(HMA_val, row[4])
            curr_psar_state = PSAR_position(PSAR_holder[CANDLES], row[4])
            print(f"HMA: {HMA_val}")
            print(f"Price: {row[4]}")
            WINDOW -= 1
            HMA_holder = HMA_holder[1:]
            print(curr_hma_state, curr_hma_state)
            if curr_hma_state != prev_hma_state and curr_hma_state == True:
                hma_cross = True
            if curr_psar_state == True and curr_hma_state == True and BUY is False:
                BUY = True
                BUY_PRICE = float(row[4])

            if BUY:
                percent_change = (float(row[4]) - BUY_PRICE) / BUY_PRICE * 100
                # print(BUY_PRICE)
                # print(percent_change)

                if percent_change >= 3:
                    WIN += 1
                    BUY = False
                    TRIALS += 1
                
                if percent_change <= -3:
                    BUY = False
                    TRIALS += 1
                    
            prev_hma_state = curr_hma_state

    print(f"Number of Trials: {TRIALS}")
    print(f"Number of Candles: {CANDLES}")
    print(f"Number of Wins {WIN}")
    print(f"Winrate: {(WIN / TRIALS) * 100:.2f}%")
    # print(f"PSAR Data:{PSAR_holder}")


        
