
import csv
import time
from collections import deque
from SimulatorCalculations import PSAR, get_PSAR_Data, PSAR_position, HMA, HMA_position, calc_stats, print_stats
from SimulatorAvgStats import AverageStats, print_averages

def get_probabilties(df, tp, sl, bal=1000):

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
        first_close = 0
        current_close = 0

        # Start simulator
        for row in reader:
            
            current_close = float(row[4])
            HMA_window.append(current_close)
            if CANDLES == 0: 
                first_close = current_close

            CANDLES += 1

            if len(HMA_window) == HMA_window.maxlen:
                # Now we have enough data to calculate HMA
                HMA_val = HMA(list(HMA_window), len(HMA_window) - 2)  
                curr_hma_state = HMA_position(HMA_val, current_close)
                curr_super_state = True if row[5] != "NaN" else False
                curr_psar_state = PSAR_position(PSAR_holder[CANDLES-1], current_close)

                # if uptrend set super state to True
                curr_super_state = True if row[5] != "NaN" else False

                if curr_psar_state and curr_hma_state and not BUY:
                    BUY = True
                    BUY_PRICE = current_close

                if BUY:
                    percent_change_high = (float(row[2]) - BUY_PRICE) / BUY_PRICE * 100
                    percent_change_low = (float(row[3]) - BUY_PRICE) / BUY_PRICE * 100

                    if percent_change_high >= tp:
                        WIN += 1
                        BUY = False
                        TRIALS += 1
                    
                    if percent_change_low <= sl:
                        BUY = False
                        TRIALS += 1
        
        return WIN / TRIALS




        
get_probabilties('./data/XRPUSDT15-SUPER-1.csv', 1, -9, bal=1000)