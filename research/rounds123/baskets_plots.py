import numpy as np
import matplotlib.pyplot as plt
import pandas as pd

#{0: (144.22, 562.0), 1: (188.48, 632.0), 2: (188.855, 570.5)}
input_folder = "backtest/new_data/"
days = [0,1,2]
# for day in days:
day = 1
plot_spread = True
file_name = f"prices_round_3_day_{day}.csv"
trades_file = f"trades_round_3_day_{day}_nn.csv"
prices = pd.read_csv(input_folder + file_name, sep = ";")
trades = pd.read_csv(input_folder + trades_file, sep = ";")

good_cols = ['timestamp', 'product', 'bid_price_1', "ask_price_1", 'mid_price']
data = prices.loc[:,good_cols]
data["diff"] = data["ask_price_1"] - data["bid_price_1"]
bids = data.pivot(index = "timestamp", columns = "product", values = "bid_price_1")
asks = data.pivot(index = "timestamp", columns = "product", values = "ask_price_1")
diffs = data.pivot(index = "timestamp", columns = "product", values = "diff")
data = data.pivot(index = "timestamp", columns = "product", values = "mid_price")
# data.cols: 'CHOCOLATE', 'GIFT_BASKET', 'ROSES', 'STRAWBERRIES'
#basket -1rose - 4chocolate - 6strawberies
coefs = [1.00, 4, 4.33]
# coefs = [1, 4, 6]
tss = diffs[diffs["GIFT_BASKET"]<2].index.values

prices[prices["product"]=="STRAWBERRIES"].loc[:,["timestamp", "bid_price_1", "ask_price_1", "ask_volume_1", "bid_volume_1"]].head(40)

product = "GIFT_BASKET"
bids[product].plot()
asks[product].plot()
for ts in tss:
	plt.axvline(x = ts, color = "r", linestyle = "--")

# data.plot(subplots = True, figsize = (10,10))
spread_bid = bids["GIFT_BASKET"] - coefs[0]*asks["ROSES"] - coefs[1]*asks["CHOCOLATE"] - coefs[2]*asks["STRAWBERRIES"]
spread_ask = asks["GIFT_BASKET"] - coefs[0]*bids["ROSES"] - coefs[1]*bids["CHOCOLATE"] - coefs[2]*bids["STRAWBERRIES"]
spread =data["GIFT_BASKET"] - coefs[0]*data["ROSES"] - coefs[1]*data["CHOCOLATE"] - coefs[2]*data["STRAWBERRIES"]

spread = pd.DataFrame({"mid": spread, "spread_bid": spread_bid, "spread_ask": spread_ask})
spread.plot()


spread["diff"] = (spread["spread_ask"] - spread["spread_bid"])
(spread["spread_ask"] - spread["spread_bid"]).describe()
(spread["spread_ask"] - spread["spread_bid"]).plot()
tss = data[spread["diff"]<22].index.values
if plot_spread:
	spread_thresholds = [342.56, 418.52]
	spread =data["GIFT_BASKET"] - coefs[0]*data["ROSES"] - coefs[1]*data["CHOCOLATE"] - coefs[2]*data["STRAWBERRIES"]
	spread.plot()
	#plot spread thresholds
	for threshold in spread_thresholds:
		plt.axhline(y = threshold, color = "r")


#gift_baskets
product = "GIFT_BASKET"
prices[prices["product"]==product].set_index("timestamp")[["bid_price_1", "ask_price_1"]].plot()
#timestamps when spread <=2
s1 = prices[prices["product"]==product]
s1["diff"] = s1["ask_price_1"] - s1["bid_price_1"]
tss = s1[s1["diff"]<=2]["timestamp"].values



data[product].plot()
#vertical lines for tss
for ts in tss:
	plt.axvline(x = ts, color = "r", linestyle = "--")
	
cov_data = data.copy()
cov_data["CHOCOLATE"] = data["CHOCOLATE"]*4
cov_data["STRAWBERRIES"] = data["STRAWBERRIES"]*6
cov_data.diff().cov()
