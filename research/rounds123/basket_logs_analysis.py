import matplotlib.pyplot as plt
import pandas as pd
pd.set_option('display.max_columns', None)
pd.set_option('display.max_rows', None)
pd.set_option('display.width', 300)
folder = "logs_data/"
basket_logs = pd.read_csv(folder + "basket_logs.csv", sep = ";")
prices = pd.read_csv(folder + "prices_basket.csv", sep = ";")
prices["diff"] = prices["ask_price_1"] - prices["bid_price_1"]
trades = pd.read_csv(folder + "trades_basket.csv", sep = ";")

good_cols = ['timestamp', 'product', 'bid_price_1', "ask_price_1", 'mid_price']
good_products = ["GIFT_BASKET", "ROSES", "CHOCOLATE", "STRAWBERRIES"]
data = prices.loc[:, good_cols]
data = data[data["product"].isin(good_products)]
data["diff"] = data["ask_price_1"] - data["bid_price_1"]
data = data.pivot(index = "timestamp", columns = "product", values = "mid_price")
data["spread"] = data["GIFT_BASKET"] - 0.94*data["ROSES"] - 3.75*data["CHOCOLATE"] - 4.30*data["STRAWBERRIES"]
data["spread"].plot()
pos = basket_logs["lambdaLog"].iloc[1:].apply(lambda x: x.split(" ")[-1])
time = basket_logs["lambdaLog"].iloc[1:].apply(lambda x: x.split(" ")[1][:-1])
pos = pd.DataFrame({"time": time, "pos": pos}).astype(int)
condition = (trades["symbol"]=="GIFT_BASKET") & (trades["buyer"]!="SUBMISSION") & (trades["seller"]!="SUBMISSION")
trades_basket = trades[condition].rename(columns = {"symbol": "product"}).merge(prices[["timestamp", "product", "mid_price", "diff"]],on = ["timestamp", "product"])
trade_time = trades[condition]["timestamp"].values
diffs = trades_basket["diff"].values
# data.plot(subplots = True, figsize = (10,10))
n = data.shape[1]
data["spread"].plot()
#plot trade times as vertival lines
spread_thresholds = [342.56, 418.52]

	
