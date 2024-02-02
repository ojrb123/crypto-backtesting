import csv
import ta_py as ta

# Returns a datasets PSAR
# data -- An array of arrays where the sub arrays contain the [[high, low]]
# step -- default to 0.02
# max -- default to 0.2
def PSAR(data, step=0.02, max=0.2):

    return ta.psar(data, step, max)

# get the required data for PSAR calculation
def get_PSAR_Data(data, psar_data=None):
    if psar_data is None:
        psar_data = []
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

# Returns a datasets HMA
# data -- An array of candle close prices [close, close]
# length -- The window size to use in the calculation
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


# Returns a datasets supertrend BUY value
# data -- An array of arrays where the sub arrays contain the [[high, close, low]]
def SuperTrend_up(data, length=3, multiplier=0.5):

    return ta.supertrend(data, length, multiplier)[0][0]

def print_stats(CANDLES, TRIALS, WIN, WINRATE, TRADES_PER_DAY, WINS_PER_DAY, EXPECTED, DAILY_VALUE):
    print(f"Number of Candles: {CANDLES}")
    print(f"Number of Trials: {TRIALS}")
    print(f"Number of Wins {WIN}")
    print(f"Winrate: {WINRATE:.2f}%")
    print(f"Trades per day: {TRADES_PER_DAY:.2f}")
    print(f"Wins per day: {WINS_PER_DAY:.2f}")
    print(f"Expected Value: {EXPECTED:.2f}")
    print(f"Daily Value: {DAILY_VALUE:.2f}")
    # print(f"Run time: {time.time() - start_time:.2f}s")

def calc_stats(WIN, TRIALS, TAKE_PROFIT, STOP_LOSS, CANDLES):
    EXPECTED = ((WIN / TRIALS) * TAKE_PROFIT) + ((1 - (WIN / TRIALS)) * STOP_LOSS)
    TRADES_PER_DAY = TRIALS / ((CANDLES / 4) / 24)
    WINRATE = (float(WIN) / float(TRIALS)) * 100
    WINS_PER_DAY = WIN / ((CANDLES / 4) / 24)
    DAILY_VALUE = EXPECTED * TRADES_PER_DAY
    return EXPECTED, TRADES_PER_DAY, WINRATE, WINS_PER_DAY, DAILY_VALUE

