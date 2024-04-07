import optuna

from backtester_logic import simulate_alternative
from consts import TRAINING_DATA_PREFIX
import os
import pandas as pd



from stupidon import Trader


max_time = 9  # int(input("Max timestamp (1-9)->(1-9)(00_000) or exact number): ") or 999000)
if max_time < 10:
    max_time *= 100000
round_ = 0  # int(input("Input a round (blank for 4): ") or 4)
day = -2  # int(input("Input a day (blank for random): ") or random.randint(1, 3))
names_in = "n"  # input("With bot names (default: y) (y/n): ")
names = True
if 'n' in names_in:
    names = False
halfway_in = "n"  # input("Matching orders halfway (default: n) (y/n): ")
halfway = False
if 'y' in halfway_in:
    halfway = True
print(f"Running simulation on round {round_} day {day} for time {max_time}")

prices_path = os.path.join(TRAINING_DATA_PREFIX, f'prices_round_{round_}_day_{day}.csv')
df_prices = pd.read_csv(prices_path, sep=';')
trades_path = os.path.join(TRAINING_DATA_PREFIX, f'trades_round_{round_}_day_{day}_wn.csv')
if not names:
    trades_path = os.path.join(TRAINING_DATA_PREFIX, f'trades_round_{round_}_day_{day}_nn.csv')
df_trades = pd.read_csv(trades_path, sep=';', dtype={'seller': str, 'buyer': str})



def objective_function(trial):
    buy_margin = trial.suggest_uniform('buy_margin', 0, 10)
    sell_margin = trial.suggest_uniform('sell_margin', 0, 10)
    time_window = trial.suggest_uniform('time_window', 0, 20)

    curr_trader = Trader(buy_margin=buy_margin, sell_margin=sell_margin, time_window=time_window)

    profits = simulate_alternative(round_, day, curr_trader, max_time, names, halfway=halfway, df_trades=df_trades,
                                   df_prices=df_prices, verbose=False, plotting=False, logging=False)

    # profits = simulate_alternative(round_, day, curr_trader, max_time, names, halfway=halfway,
    #                                verbose=False, plotting=False, logging=False)

    result = 0
    for profit in profits.values():
        result += profit

    return result


if __name__ == "__main__":

    study = optuna.create_study(direction='maximize')

    n_jobs = 8
    study.optimize(objective_function, n_trials=100, n_jobs=n_jobs, show_progress_bar=True)

    print(f"Best parameters: {study.best_params}")

    trader = Trader(**study.best_params, verbose=True)
    profits = simulate_alternative(round_, day, trader, max_time, names, halfway=halfway)
    print(f"Profits: {profits}")
