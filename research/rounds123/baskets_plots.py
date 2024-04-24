import numpy as np
import matplotlib.pyplot as plt
import pandas as pd

#{0: (144.22, 562.0), 1: (188.48, 632.0), 2: (188.855, 570.5)}
input_folder = "backtest/new_data/"
days = [0,1,2]
# for day in days:
day = 0
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
mids = data.pivot(index = "timestamp", columns = "product", values = "mid_price")
mids.diff().dropna()
# data.cols: 'CHOCOLATE', 'GIFT_BASKET', 'ROSES', 'STRAWBERRIES'
#basket -1rose - 4chocolate - 6strawberies
# coefs = [1.00, 3.71, 4.38]
coefs = [1, 4, 6]
mids["spread"] = mids["GIFT_BASKET"] - coefs[0]*mids["ROSES"] - coefs[1]*mids["CHOCOLATE"] - coefs[2]*mids["STRAWBERRIES"]
def time_reg(x):
	time = np.linspace(0, len(x), len(x))
	coef = np.linalg.lstsq(time.reshape(-1,1), x-x.mean(), rcond = None)[0]*3
	return coef[0] * len(x) + np.median(x)

hist_len = 40
fee = 30


#plot fee on subplots
fig, ax = plt.subplots(1,1)
mids["spread"].plot(label = "spread", ax = ax)
md = mids["spread"].rolling(hist_len).apply(lambda x: time_reg(x))
# fee = (mids["spread"] - md).rolling(hist_len).std()*1.0
md.plot(label = "median", ax = ax)
(md+ fee).plot(label = "median + fee", ax = ax)
(md- fee).plot(label = "median - fee", ax = ax)
