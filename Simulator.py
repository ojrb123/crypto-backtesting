import pandas as pd 
import ta_py as ta;
import csv
import time
from SimulatorCalculations import PSAR, get_PSAR_Data, PSAR_position, HMA, HMA_position, initial_hma, SuperTrend, calc_stats, print_stats
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
        next(reader)
        HMA_holder = []
        PSAR_data = []
        PSAR_data = get_PSAR_Data(df)
        PSAR_holder = []
        PSAR_holder = PSAR(PSAR_data)
        WINDOW = 0 
        TRIALS = 0
        CANDLES = 0
        BUY = False
        BUY_PRICE = 0.00
        WIN = 0
        
        # prev_hma_state = True
        prev_psar_state = True
        initial_hma_val, last_close_for_hma = initial_hma(df, 11)

        # Set prev_hma_state based on the comparison
        prev_hma_state = last_close_for_hma > initial_hma_val[0]  # Assuming HMA function returns a list or similar
        for _ in range(8): 
            next(reader)

        for row in reader:
            HMA_holder.append(row[4])
            WINDOW += 1
            CANDLES += 1
            if WINDOW == 11:
                HMA_val = HMA(HMA_holder, WINDOW-2)
                curr_hma_state = HMA_position(HMA_val, row[4])
                # print(f"curr hma state: {curr_hma_state}")
                curr_psar_state = PSAR_position(PSAR_holder[CANDLES-1], row[4])
    
                WINDOW -= 1
                HMA_holder = HMA_holder[1:]

                if curr_hma_state != prev_hma_state and curr_hma_state == True:
                    hma_cross = True
                if curr_psar_state == True and curr_hma_state == True and BUY is False:
                    BUY = True
                    BUY_PRICE = float(row[4])

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

        
