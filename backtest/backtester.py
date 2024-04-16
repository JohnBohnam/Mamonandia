import sys
sys.path.append("..")
# from traders.amethyst_MM import Trader
# from traders.stupidon import Trader
# from bot_with_exercised_trades import Trader
from backtester_logic import simulate_alternative
from traders.get_limits import Trader
import time

# Adjust accordingly the round and day to your needs
if __name__ == "__main__":
    curr_trader = Trader()
    max_time = 1  # int(input("Max timestamp (1-9)->(1-9)(00_000) or exact number): ") or 999000)
    if max_time < 10:
        max_time *= 100000
    round_ = 3  # int(input("Input a round (blank for 4): ") or 4)
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
    day = 1
    max_time = 10000
    print(f"Running simulation on round {round_} day {day} for time {max_time}")
    profits = simulate_alternative(round_, day, curr_trader, max_time, names, verbose=False, plotting=True, logging=False)
    print(f"profits: {profits}")

