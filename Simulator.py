
import csv
import time
from collections import deque
from SimulatorCalculations import PSAR, get_PSAR_Data, PSAR_position, HMA, HMA_position, calc_stats, print_stats
from SimulatorAvgStats import AverageStats, print_averages

datafeeds = ['./data/LINKUSDT15-SUPER-1.csv', './data/LINKUSDT15-SUPER-2.csv',
            './data/SNXUSDT15-SUPER-1.csv','./data/SNXUSDT15-SUPER-2.csv',
            './data/LTCUSDT15-SUPER-1.csv', './data/DOTUSDT15-SUPER-1.csv',
            './data/DOTUSDT15-SUPER-2.csv', './data/AVAXUSDT15-SUPER-1.csv',
            './data/ENJUSDT15-SUPER-1.csv', './data/ETHUSDT15-SUPER-1.csv',
            './data/ALGOUSDT15-SUPER-1.csv', './data/BNBUSDT15-SUPER-1.csv',
            './data/DOGEUSDT15-SUPER-1.csv', './data/ONEUSDT15-SUPER-1.csv',
            './data/ADAUSDT15-SUPER-1.csv', './data/EGLDUSDT15-SUPER-1.csv',
            './data/MATICUSDT15-SUPER-1.csv', './data/PYTHUSDT15-SUPER-1.csv',
            './data/TIAUSDT15-SUPER-1.csv', './data/SOLUSDT15-SUPER-1.csv',
            './data/XRPUSDT15-SUPER-1.csv']

# custom vars


starting_time = time.time()
average_stats = AverageStats()

def run_simulation(df, tp, sl, bal=1000):
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

                curr_psar_state = PSAR_position(PSAR_holder[CANDLES-1], current_close)

                # if uptrend set super state to True
                curr_super_state = True if row[5] != "NaN" else False

                if curr_psar_state and curr_hma_state and not BUY:
                    BUY = True
                    BUY_PRICE = current_close

                if BUY:
                    percent_change = (float(row[4]) - BUY_PRICE) / BUY_PRICE * 100

              
                    if percent_change >= tp:
                        WIN += 1
                        BUY = False
                        TRIALS += 1
                    
                    if percent_change <= sl:
                        BUY = False
                        TRIALS += 1

        TO_BEAT = (current_close - first_close) / first_close * 100
        EXPECTED, TRADES_PER_DAY, WINRATE, WINS_PER_DAY, DAILY_VALUE, TO_BEAT_BALANCE, END_BALANCE = calc_stats(WIN, TRIALS, tp, sl, CANDLES, TO_BEAT, bal)
        print_stats(CANDLES, TRIALS, WIN, WINRATE, TRADES_PER_DAY, WINS_PER_DAY, EXPECTED, DAILY_VALUE, TO_BEAT_BALANCE, END_BALANCE)
        average_stats.update_stats(CANDLES, TRIALS, WIN, WINRATE, TRADES_PER_DAY, WINS_PER_DAY, EXPECTED, DAILY_VALUE, TO_BEAT_BALANCE, END_BALANCE)
        
        return CANDLES, TRIALS, WIN, WINRATE, TRADES_PER_DAY, WINS_PER_DAY, EXPECTED, DAILY_VALUE, TO_BEAT_BALANCE, END_BALANCE

if __name__ == '__main__':
    
    
    for df in datafeeds:
        coin_name = df.split('/')[-1].split('USDT')[0]
        print(f"-----------{coin_name}-----------")
        run_simulation(df, 5, -1)

    averages = average_stats.calculate_averages()
    print_averages(averages)
    print(average_stats.get_average_sim_winrate())

    print("---------------OTHER---------------")
    print(f"Run time: {time.time() - starting_time:.2f}s")

        
