import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from statsmodels.tsa.vector_ar.vecm import coint_johansen
from statsmodels.tsa.stattools import coint
import statsmodels.api as sm
days = [1,2,3]
folder = "backtest/new_data/"
# for day in days:
day = 2
prices = pd.read_csv(folder + f"prices_round_4_day_{day}.csv", sep = ";")
good_cols = ['timestamp', 'product', 'bid_price_1', "ask_price_1", 'mid_price']
prices = prices.loc[:, good_cols]
prices["timestamp"]  =prices["timestamp"]/100
prices["bid_ask_spread"] = prices["ask_price_1"] - prices["bid_price_1"]
spreads = prices.pivot(index = "timestamp", columns = "product", values = "bid_ask_spread")
mids = prices.pivot(index = "timestamp", columns = "product", values = "mid_price")
diffs = prices.pivot(index = "timestamp", columns = "product", values = "mid_price").diff().dropna()
# print(mids.shape)
X = diffs[["COCONUT"]].values
X = sm.add_constant(X)
y = diffs["COCONUT_COUPON"].values
model = sm.OLS(y, X)
results = model.fit()
print("printing results")
print(results.params)
diffs["spread"] = (1.29 * diffs["COCONUT"] - diffs["COCONUT_COUPON"]) / 2.29
cov = diffs.cov()
# diffs["spread"].rolling(100).sum().plot()
# coef = cov.loc["COCONUT_COUPON", "COCONUT"]/cov.loc["COCONUT", "COCONUT"]
coef =0.5
diffs["pure_coupon"] = diffs["COCONUT_COUPON"] - coef * diffs["COCONUT"]
print(cov)
# mids["spread"].rolling(100).sum().plot()
# diffs["pure_coupon"].rolling(1000).mean().plot()
# diffs["pure_coupon"].rolling(100).mean().plot()
# (diffs["pure_coupon"].cumsum()-4060).plot()
#cumulated median
# diffs["pure_coupon"].rolling(100).mean().plot()
(mids["COCONUT_COUPON"] - coef * mids["COCONUT"]).plot()
(mids["COCONUT_COUPON"] - coef * mids["COCONUT"]).rolling(1000).median().plot()
(mids["COCONUT_COUPON"] - coef * mids["COCONUT"]+20).rolling(1000).median().plot()
(mids["COCONUT_COUPON"] - coef * mids["COCONUT"]-20).rolling(1000).median().plot()
# mids.pure_coconut.rolling(100).sum().plot()
# mids.pure_coconut.rolling(50).sum().plot()
# plt.scatter(mids["COCONUT_COUPON"], mids["COCONUT"])
# 1,41x2 - 2*0.56*x + 1.06

# x = 0.56/1.06