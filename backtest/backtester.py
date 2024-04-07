# from one_day_Trader import Trader
from plotters import Plotter
# from Strategy2023.trader import Trader
from datamodel import *
import pandas as pd
import statistics
import copy
import uuid
import os
from datetime import datetime

from consts import *

from stupidon import Trader
from backtester_logic import simulate_alternative

# Adjust accordingly the round and day to your needs
if __name__ == "__main__":
    curr_trader = Trader()
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

    profits = simulate_alternative(round_, day, curr_trader, max_time, names, halfway=halfway,
                                   df_trades=df_trades, df_prices=df_prices,
                                   verbose=False, plotting=False, logging=False)
    print(f"profits: {profits}")
