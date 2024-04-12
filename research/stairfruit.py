import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import os
from traders.ml_trader import *

pd.set_option('display.max_columns', None)
days = [-2, -1, 0]
round = 1
product = "STARFRUIT"
folder = "backtest/new_data"
prices_path = {day:os.path.join(folder, f"prices_round_{round}_day_{day}.csv") for day in days}
trades_path = {day:os.path.join(folder, f"trades_round_{round}_day_{day}_nn.csv") for day in days}

def read_data(path, prod_name):
	data = pd.read_csv(path, sep = ";")
	data["timestamp"] = data["timestamp"].astype(int)/100
	data = data[data[prod_name] == product]
	return data

prices = {day:read_data(prices_path[day], "product") for day in days}
trades = {day:read_data(trades_path[day], "symbol") for day in days}
day = -1
df = prices[day]
n_prev = 5


colls_taken = ['bid_price_1', 'bid_volume_1', 'ask_price_1', 'ask_volume_1', 'bid_volume_2', 'ask_volume_2']
df = df.loc[:,colls_taken].fillna(0).values
X = [df[(i-n_prev):i].reshape(-1) for i in range(n_prev, len(df))]
X = np.array(X)
buy_prob = bid_forward(X).reshape(-1)
sell_prob = ask_forward(X).reshape(-1)
plot_df = prices[day]
start = np.array([0]*n_prev)
plot_df["buy_prob"] = np.concatenate([start, buy_prob])
plot_df["sell_prob"] = np.concatenate([start, sell_prob])

fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 8), sharex=True)
plot_df.loc[:,["bid_price_1", "ask_price_1"]].plot(ax = ax1)
plot_df.loc[:,["buy_prob", "sell_prob"]].plot(style = {"buy_prob":"x", "sell_prob":"x"}, ax = ax2)