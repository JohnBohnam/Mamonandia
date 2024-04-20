import pandas as pd
pd.set_option('display.max_columns', None)
pd.set_option('display.width', 1000)
pd.set_option('display.max_rows', 1000)
import numpy as np
import os

product = "AMETHYSTS"
prices = pd.read_csv("logs_data/prices_from_logs.csv", sep=";")
trades = pd.read_csv("logs_data/trades_from_logs.csv", sep=";")
prices = prices[prices["product"] == product]
trades = trades[trades["symbol"] == product]
trades["timestamp"] = trades["timestamp"].astype(int)
prices["timestamp"] = prices["timestamp"].astype(int)

plot_df = prices.merge(trades.loc[:,["timestamp", "price"]], on = "timestamp", how = "left").set_index("timestamp")
plot_df.loc[:,["bid_price_1", "ask_price_1", "price"]].plot(style = {"price":"x"})
my_trades_ts = set(trades[(trades["buyer"] == "SUBMISSION") | (trades["seller"] == "SUBMISSION")]["timestamp"])
# not my trades
other_ts = trades[(trades["buyer"] != "SUBMISSION") & (trades["seller"] != "SUBMISSION")]["timestamp"].shape
trades[trades["timestamp"].isin(other_ts)]
