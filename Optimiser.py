from Simulator import run_simulation
from SimulatorAvgStats import AverageStats, print_averages
import time

starting_time = time.time()
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

# Assuming run_simulation is modified to return a win rate or a boolean indicating success/failure

def Mega_Simulation(datafeeds, balance=1000):
    # Dictionary to store average win rates for each TP and SL combination
    combination_win_rates = {}
    print("Running...")
    for tp in range(1, 8):  # Adjusted range to include 7
        for sl in range(-1, -8, -1):  # Adjusted range to include -7
            # Reset or Initialize AverageStats for each TP, SL combination
            average_stats = AverageStats()
            
            # Run simulation for each datafeed
            for df in datafeeds:
                CANDLES, TRIALS, WIN, WINRATE, TRADES_PER_DAY, WINS_PER_DAY, EXPECTED, DAILY_VALUE, TO_BEAT_BALANCE, END_BALANCE = run_simulation(df, tp, sl, balance)
                average_stats.update_stats(CANDLES, TRIALS, WIN, WINRATE, TRADES_PER_DAY, WINS_PER_DAY, EXPECTED, DAILY_VALUE, TO_BEAT_BALANCE, END_BALANCE)
                
            # Calculate the average win rate for this TP, SL combination
            avg_sim_winrate = average_stats.get_average_sim_winrate()
            
            # Store the result
            combination_win_rates[(tp, sl)] = avg_sim_winrate

    

    # Print out the results at the end
    print("TP, SL Combinations and Their Average Simulation Win Rates:")
    for combination, win_rate in combination_win_rates.items():
        print(f"TP: {combination[0]}, SL: {combination[1]}, Win Rate: {win_rate}%")

    # Optionally, find and print the best combination
    best_combination = max(combination_win_rates, key=combination_win_rates.get)
    print(f"Best Combination: TP: {best_combination[0]}, SL: {best_combination[1]}, Win Rate: {combination_win_rates[best_combination]}%")

    print(f"Total Run Time: {time.time() - starting_time:.2f}s")

Mega_Simulation(datafeeds)