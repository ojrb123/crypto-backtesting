import ta_py as ta;
import csv
import time
from collections import deque
from SimulatorCalculations import PSAR, get_PSAR_Data, PSAR_position, HMA, HMA_position, initial_hma, SuperTrend_up, calc_stats, print_stats
from SimulatorAvgStats import AverageStats, print_averages

LINKdf = './data/LINK-USDT15.csv'
SNXdf = './data/SNX-USDT15.csv'
LTCdf = './data/LTC-USDT15.csv'
DOTdf = './data/DOT-USDT15.csv'
AVAXdf = './data/AVAX-USDT15.csv'

# custom vars
TAKE_PROFIT = 5
STOP_LOSS = -5

starting_time = time.time()
average_stats = AverageStats()

def run_simulation(df):
    with open(df, 'r') as csv_file:
        reader = csv.reader(csv_file)
        next(reader)  # Skip header

        # Initialize the sliding window for HMA calculation
        HMA_window = deque(maxlen=11)  

        # Init the PSAR array
        PSAR_data = get_PSAR_Data(df)
        PSAR_holder = PSAR(PSAR_data)
        
        # Reset simulator state
        TRIALS = 0
        CANDLES = 0
        BUY = False
        WIN = 0

        for row in reader:
            current_close = float(row[4])
            HMA_window.append(current_close)
            CANDLES += 1

            if len(HMA_window) == HMA_window.maxlen:
                # Now we have enough data to calculate HMA
                HMA_val = HMA(list(HMA_window), len(HMA_window) - 2)  
                curr_hma_state = HMA_position(HMA_val, current_close)
                curr_psar_state = PSAR_position(PSAR_holder[CANDLES-1], current_close)

                if curr_psar_state and curr_hma_state and not BUY:
                    BUY = True
                    BUY_PRICE = current_close

                if BUY:
                    percent_change = (float(row[4]) - BUY_PRICE) / BUY_PRICE * 100

                    if percent_change >= TAKE_PROFIT:
                        WIN += 1
                        BUY = False
                        TRIALS += 1
                    
                    if percent_change <= STOP_LOSS:
                        BUY = False
                        TRIALS += 1
                        
                prev_hma_state = curr_hma_state

        EXPECTED, TRADES_PER_DAY, WINRATE, WINS_PER_DAY, DAILY_VALUE = calc_stats(WIN, TRIALS, TAKE_PROFIT, STOP_LOSS, CANDLES)
        print_stats(CANDLES, TRIALS, WIN, WINRATE, TRADES_PER_DAY, WINS_PER_DAY, EXPECTED, DAILY_VALUE)
        average_stats.update_stats(CANDLES, TRIALS, WIN, WINRATE, TRADES_PER_DAY, WINS_PER_DAY, EXPECTED, DAILY_VALUE)

print("---------------LINK---------------")
run_simulation(LINKdf)

print("---------------SNX---------------")
run_simulation(SNXdf)

print("---------------LTC---------------")
run_simulation(LTCdf)

print("---------------DOT---------------")
run_simulation(DOTdf)

print("---------------AVAX---------------")
run_simulation(AVAXdf)

averages = average_stats.calculate_averages()
print_averages(averages)

print("---------------OTHER---------------")
print(f"Run time: {time.time() - starting_time:.2f}s")

        
