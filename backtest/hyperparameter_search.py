import sys

sys.path.append("..")

import optuna

from backtester_logic import simulate_alternative
from consts import TRAINING_DATA_PREFIX
import os
import pandas as pd

from traders.rounds123.bot_with_exercised_trades import Trader

max_time = 1  # int(input("Max timestamp (1-9)->(1-9)(00_000) or exact number): ") or 999000)
if max_time < 10:
    max_time *= 100000
round_ = 1  # int(input("Input a round (blank for 4): ") or 4)
day = -2  # int(input("Input a day (blank for random): ") or random.randint(1, 3))
names_in = "n"  # input("With bot names (default: y) (y/n): ")
names = True
if 'n' in names_in:
    names = False

prices_path = os.path.join(TRAINING_DATA_PREFIX, f'prices_round_{round_}_day_{day}.csv')
df_prices = pd.read_csv(prices_path, sep=';')
trades_path = os.path.join(TRAINING_DATA_PREFIX, f'trades_round_{round_}_day_{day}_wn.csv')
if not names:
    trades_path = os.path.join(TRAINING_DATA_PREFIX, f'trades_round_{round_}_day_{day}_nn.csv')
df_trades = pd.read_csv(trades_path, sep=';', dtype={'seller': str, 'buyer': str})


def objective_function(trial):
    buy_margin = trial.suggest_int('buy_margin', 0, 7)
    sell_margin = trial.suggest_int('sell_margin', 0, 7)
    time_window = trial.suggest_int('time_window', 1, 30)
    # mean_exponent = trial.suggest_float('mean_exponent', 0.5, 4)

    curr_trader = Trader(buy_margin=buy_margin, sell_margin=sell_margin, time_window=time_window,
                         verbose=False)

    profits = simulate_alternative(round_, day, curr_trader, max_time, names, df_trades=df_trades,
                                   df_prices=df_prices, verbose=False, plotting=False, logging=False)

    # profits = simulate_alternative(round_, day, curr_trader, max_time, names, halfway=halfway,
    #                                verbose=False, plotting=False, logging=False)

    result = 0
    for profit in profits.values():
        result += profit

    return result


if __name__ == "__main__":
    study = optuna.create_study(direction='maximize')

    n_jobs = 1
    study.optimize(objective_function, n_trials=500, n_jobs=n_jobs, show_progress_bar=True)

    trader = Trader(**study.best_params, verbose=False)
    profits = simulate_alternative(round_, day, trader, 900000, names, verbose=False, plotting=False, logging=False)
    print(f"Profits: {profits}")

    print(f"Best parameters: {study.best_params}")
    # {'buy_margin': 0.7850037515086065, 'sell_margin': 0.6388820974848624, 'time_window': 6.469020211030575}
    # {'buy_margin': 8.62918163605573, 'sell_margin': 5.470549505892109, 'time_window': 3.6582073498143353}

    # {'buy_margin': 4, 'sell_margin': 3, 'time_window': 5, 'mean_exponent': 2.5872384380550466}
    # {'buy_margin': 4, 'sell_margin': 3, 'time_window': 3, 'mean_exponent': 2.3163307967879034}
