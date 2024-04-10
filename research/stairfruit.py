import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import os
days = [-2, -1, 0]
round = 1
product = "AMETHYSTS"
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
day = 0
prices[day]["mid_price_rolling_median"] = prices[day]["mid_price"].rolling(6).median()
plot_df = prices[day].merge(trades[day].loc[:,["timestamp", "price"]], on = "timestamp", how = "left").set_index("timestamp")
plot_df.plot(y = ["price", "bid_price_1", "ask_price_1"], figsize = (20, 10), style = {"price":"x"})

for day in days:
	print(day, prices[day]["mid_price"].mean())

