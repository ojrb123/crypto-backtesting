
import csv
import time
from collections import deque
from SimulatorCalculations import PSAR, get_PSAR_Data, PSAR_position, HMA, HMA_position, calc_stats, print_stats
from SimulatorAvgStats import AverageStats, print_averages
from SimulatorProbablities import get_probabilties
from math import ceil

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

def run_simulation(df, tp, sl, prob_increase, bal=1000):

    fraction = (prob_increase / (abs(sl) / 100)) - ((1 - prob_increase) / (tp / 100))
    leverage = fraction / abs(sl) if fraction > 0 else 1
    leverage = 1 if leverage < 1 else ceil(leverage)
    fraction = 1 if fraction < 1 else fraction

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

                    bet_amount = bal / (abs(sl) / fraction)
    
                    if percent_change_high >= tp:
                        WIN += 1
                        BUY = False
                        TRIALS += 1
                        profit = bet_amount * (tp / 100)
                        bal += profit
                        # print("\033[32m" + f"Trade Won, Gained ${profit:.2f}, Balance: ${bal:.2f}, Price increase: {percent_change_high:.2f}%, Date: {row[0]}, Buy Price: {BUY_PRICE}, Sell Price: {current_close}" + "\033[37m")
                    
                    if percent_change_low <= sl:
                        BUY = False
                        TRIALS += 1
                        loss = bet_amount * (abs(sl) / 100)
                        bal -= loss
                        # print("\033[31m" + f"Trade Lost, Lost ${loss:.2f}, Balance: ${bal:.2f}, Price decrease: {percent_change_low:.2f}%, Date: {row[0]}, Buy Price: {BUY_PRICE}, Sell Price: {current_close}" + "\033[37m")

        TO_BEAT = (current_close - first_close) / first_close * 100
        EXPECTED, TRADES_PER_DAY, WINRATE, WINS_PER_DAY, DAILY_VALUE, TO_BEAT_BALANCE, END_BALANCE = calc_stats(WIN, TRIALS, tp, sl, CANDLES, TO_BEAT, 1000)
        print_stats(CANDLES, TRIALS, WIN, WINRATE, TRADES_PER_DAY, WINS_PER_DAY, EXPECTED, DAILY_VALUE, TO_BEAT_BALANCE, bal)
        print(f"Kellys Fraction: {fraction:.2f}, Leverage: {leverage:.2f}")
        # print(f"To Beat: ${TO_BEAT_BALANCE:.2f}")
        # print(f"End Balance: ${bal:.2f}")
        average_stats.update_stats(CANDLES, TRIALS, WIN, WINRATE, TRADES_PER_DAY, WINS_PER_DAY, EXPECTED, DAILY_VALUE, TO_BEAT_BALANCE, bal)
        
        return CANDLES, TRIALS, WIN, WINRATE, TRADES_PER_DAY, WINS_PER_DAY, EXPECTED, DAILY_VALUE, TO_BEAT_BALANCE, bal

if __name__ == '__main__':
    

    for df in datafeeds:
            prob_increase = get_probabilties(df, 1, -3)
            coin_name = df.split('/')[-1].split('USDT')[0]
            print(f"-----------{coin_name}-----------")
            run_simulation(df, 1, -3, prob_increase)

    averages = average_stats.calculate_averages()
    print_averages(averages)

    print("---------------OTHER---------------")
    print(f"Run time: {time.time() - starting_time:.2f}s")

        
