import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from statsmodels.tsa.vector_ar.vecm import coint_johansen
from statsmodels.tsa.stattools import coint
import statsmodels.api as sm
days = [1,2,3]
folder = "backtest/new_data/"
for day in days:
# day = 1
	prices = pd.read_csv(folder + f"prices_round_4_day_{day}.csv", sep = ";")
	good_cols = ['timestamp', 'product', 'bid_price_1', "ask_price_1", 'mid_price']
	prices = prices.loc[:, good_cols]
	mids = prices.pivot(index = "timestamp", columns = "product", values = "mid_price").reset_index()
	mids["COCONUT_COUPON"] = mids["COCONUT_COUPON"] - 600
	mids["COCONUT"] = mids["COCONUT"] - 10000
	mids = mids[mids["COCONUT"]>0]
	# print(mids.shape)
	if mids.shape[0] == 0:
		continue
	X = mids[[ "COCONUT"]].values
	X = sm.add_constant(X)
	y = mids["COCONUT_COUPON"].values
	model = sm.OLS(y, X)
	results = model.fit()
	print(results.params)
	
	# plt.scatter(mids["COCONUT_COUPON"], mids["COCONUT"])