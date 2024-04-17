import numpy as np
import matplotlib.pyplot as plt
import pandas as pd


input_folder = "backtest/new_data/"
days = [0,1,2]
result = {}


def maximize_profit(prices):
	max_profit = 0
	result = (0, 0)
	buy_threshold = 0
	sell_threshold = 0
	min_price = min(prices)
	max_price = max(prices)
	best_counter = 0
	for buy_perc in range(1, 100):  # Buy threshold from 1% to 99%
		
		for sell_perc in range(buy_perc + 1, 101):  # Sell threshold from buy_perc + 1 to 100%
			buy_threshold = min_price + (max_price - min_price) * buy_perc / 100
			sell_threshold = min_price + (max_price - min_price) * sell_perc / 100
			bought = False
			sold = False
			profit = 0
			counter = 0
			for price in prices:
				
				#buy below threshold
				if not bought and price <= buy_threshold:
					#add sold
					if sold:
						profit += sell_threshold - buy_threshold
						sold = False
						counter += 1
					bought = True
				#sell above threshold
				elif not sold and price >= sell_threshold:
					#add bought
					if bought:
						profit += sell_threshold - buy_threshold
						bought = False
						counter += 1
					sold = True
			if profit > max_profit:
				max_profit = profit
				result = (buy_threshold, sell_threshold)
				best_counter = counter
	return result


#
for day in days:
	file_name = f"prices_round_3_day_{day}.csv"
	data = pd.read_csv(input_folder + file_name, sep = ";")
	gift_box_spread = data[data["product"] == "GIFT_BASKET"]
	gift_box_spread = gift_box_spread["ask_price_1"] - gift_box_spread["bid_price_1"]
	print(f'gitf_box_spread: {gift_box_spread.median()}')
	good_cols = ['timestamp', 'product', 'mid_price']
	data = data.loc[:,good_cols]
	# coefs = [1.00, 4, 4.33]
	coefs = [1, 4, 6]
	data = data.pivot(index = "timestamp", columns = "product", values = "mid_price")
	spread = data["GIFT_BASKET"] - coefs[0]*data["ROSES"] - coefs[1]*data["CHOCOLATE"] - coefs[2]*data["STRAWBERRIES"]
	print(spread.diff().dropna().abs().quantile(0.8))
	
	thresholds =maximize_profit(spread.values)
	print(thresholds[1] - thresholds[0])
	result[day] = thresholds
	
	

