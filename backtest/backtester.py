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

import time

# Adjust accordingly the round and day to your needs
if __name__ == "__main__":
    curr_trader = Trader(verbose=False)
    max_time = 9  # int(input("Max timestamp (1-9)->(1-9)(00_000) or exact number): ") or 999000)
    if max_time < 10:
        max_time *= 100000
    round_ = 1  # int(input("Input a round (blank for 4): ") or 4)
    # day = -2  # int(input("Input a day (blank for random): ") or random.randint(1, 3))
    names_in = "n"  # input("With bot names (default: y) (y/n): ")
    names = True
    if 'n' in names_in:
        names = False

    # for day in range(-2, 1):
    # # day = -2
    #     print(f"Running simulation on round {round_} day {day} for time {max_time}")
    #     profits = simulate_alternative(round_, day, curr_trader, max_time, names, verbose=False, plotting=False, logging=False)
    #     print(f"profits: {profits}")
    day = 0
    max_time = 999000-100
    print(f"Running simulation on round {round_} day {day} for time {max_time}")
    profits = simulate_alternative(round_, day, curr_trader, max_time, names, verbose=False, plotting=False, logging=False)
    print(f"profits: {profits}")

