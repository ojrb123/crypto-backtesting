class AverageStats:
    def __init__(self):
        self.AVG_CANDLES = 0
        self.AVG_TRIALS = 0
        self.AVG_WINS = 0
        self.AVG_WINRATE = 0
        self.AVG_TRADES_PER_DAY = 0
        self.AVG_WINS_PER_DAY = 0
        self.AVG_EXPECTED_VALUE = 0
        self.AVG_DAILY_VALUE = 0
        self.SIMULATIONS = 0

    def update_stats(self, CANDLES, TRIALS, WIN, WINRATE, TRADES_PER_DAY, WINS_PER_DAY, EXPECTED, DAILY_VALUE):
        self.AVG_CANDLES += CANDLES
        self.AVG_TRIALS += TRIALS
        self.AVG_WINS += WIN
        self.AVG_WINRATE += WINRATE
        self.AVG_TRADES_PER_DAY += TRADES_PER_DAY
        self.AVG_WINS_PER_DAY += WINS_PER_DAY
        self.AVG_EXPECTED_VALUE += EXPECTED
        self.AVG_DAILY_VALUE += DAILY_VALUE
        self.SIMULATIONS += 1

    def calculate_averages(self):
        if self.SIMULATIONS > 0:
            return {
                'Avg Candles': self.AVG_CANDLES / self.SIMULATIONS,
                'Avg Trials': self.AVG_TRIALS / self.SIMULATIONS,
                'Avg Wins': self.AVG_WINS / self.SIMULATIONS,
                'Avg Winrate': self.AVG_WINRATE / self.SIMULATIONS,
                'Avg Trades per Day': self.AVG_TRADES_PER_DAY / self.SIMULATIONS,
                'Avg Wins per Day': self.AVG_WINS_PER_DAY / self.SIMULATIONS,
                'Avg Expected Value': self.AVG_EXPECTED_VALUE / self.SIMULATIONS,
                'Avg Daily Value': self.AVG_DAILY_VALUE / self.SIMULATIONS
            }
        else:
            return {}

def print_averages(averages):
    print("---------------AVERAGE STATS---------------")
    for key, value in averages.items():
        if key == 'Avg Winrate':
            print(f"{key}: {value:.2f}%")
        else:
            print(f"{key}: {value:.2f}")
