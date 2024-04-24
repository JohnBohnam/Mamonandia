import numpy as np
import pandas as pd
pd.set_option('display.max_columns', None)
pd.set_option('display.width', 300)
pd.set_option('display.max_rows', 300)
import matplotlib.pyplot as plt

days =[1,2,3]
folder = "backtest/new_data/"
fig, ax = plt.subplots(1,1)
for day in days:
	prices = pd.read_csv(folder + f"prices_round_4_day_{day}.csv", sep = ";")
	# prices.columns = ['day', 'timestamp', 'product', 'bid_price_1', 'bid_volume_1', 'bid_price_2',
	# 'bid_volume_2', 'bid_price_3', 'bid_volume_3', 'ask_price_1', 'ask_volume_1', 'ask_price_2',
	# 'ask_volume_2', 'ask_price_3', 'ask_volume_3', 'mid_price', 'profit_and_loss']
	
	prices["timestamp"] = prices["timestamp"].astype(int)/100
	good_cols = ['timestamp', 'product', 'bid_price_1', "ask_price_1", 'mid_price']
	prices = prices.loc[:, good_cols]
	
	mids = prices.pivot(index = "timestamp", columns = "product", values = "mid_price")
	means_1 = mids.mean()
	mids["diff"] = mids["COCONUT"] - mids["COCONUT_COUPON"]
	mids["diff"].plot(label = day, ax = ax)
	print(mids.diff().corr())