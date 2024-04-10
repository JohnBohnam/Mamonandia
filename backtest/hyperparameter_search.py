import optuna

from backtester_logic import simulate_alternative
from consts import TRAINING_DATA_PREFIX
import os
import pandas as pd



from traders.bot_with_exercised_trades import Trader


max_time = 9  # int(input("Max timestamp (1-9)->(1-9)(00_000) or exact number): ") or 999000)
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
    # buy_margin = trial.suggest_uniform('buy_margin', 0, 5)
    # sell_margin = trial.suggest_uniform('sell_margin', 0, 5)
    time_window = trial.suggest_int('time_window', 0, 30)

    curr_trader = Trader(buy_margin=1, sell_margin=1, time_window=time_window)

    profits = simulate_alternative(round_, day, curr_trader, max_time, names, df_trades=df_trades.copy(),
                                   df_prices=df_prices.copy(), verbose=False, plotting=False, logging=False)

    # profits = simulate_alternative(round_, day, curr_trader, max_time, names, halfway=halfway,
    #                                verbose=False, plotting=False, logging=False)

    result = 0
    for profit in profits.values():
        result += profit

    return result


if __name__ == "__main__":

    study = optuna.create_study(direction='maximize')

    n_jobs = 8
    study.optimize(objective_function, n_trials=20, n_jobs=n_jobs, show_progress_bar=True)

    trader = Trader(**study.best_params, verbose=False)
    profits = simulate_alternative(round_, day, trader, max_time, names)
    print(f"Profits: {profits}")

    print(f"Best parameters: {study.best_params}")
    # {'buy_margin': 0.7850037515086065, 'sell_margin': 0.6388820974848624, 'time_window': 6.469020211030575}
    # {'buy_margin': 8.62918163605573, 'sell_margin': 5.470549505892109, 'time_window': 3.6582073498143353}

