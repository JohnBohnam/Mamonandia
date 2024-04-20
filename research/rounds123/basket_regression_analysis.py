import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
#{0: (144.22, 562.0), 1: (188.48, 632.0), 2: (188.855, 570.5)}
input_folder = "backtest/new_data/"
days = [0,1,2]
plot_spread = True
for day in days:
# day = 0
	file_name = f"prices_round_3_day_{day}.csv"
	data = pd.read_csv(input_folder + file_name, sep = ";")
	
	# ['day', 'timestamp', 'product', 'bid_price_1', 'bid_volume_1',
	#        'bid_price_2', 'bid_volume_2', 'bid_price_3', 'bid_volume_3',
	#        'ask_price_1', 'ask_volume_1', 'ask_price_2', 'ask_volume_2',
	#        'ask_price_3', 'ask_volume_3', 'mid_price', 'profit_and_loss']
	good_cols = ['timestamp', 'product', 'bid_price_1', "ask_price_1", 'mid_price']
	data = data.loc[:,good_cols]
	data["diff"] = data["ask_price_1"] - data["bid_price_1"]
	data = data.pivot(index = "timestamp", columns = "product", values = "mid_price")
	# data["HALF_BASKET"] = data["GIFT_BASKET"] - data["CHOCOLATE"]*4 - data["ROSES"]
	# data.cols: 'CHOCOLATE', 'GIFT_BASKET', 'ROSES', 'STRAWBERRIES'
	#basket -1rose - 4chocolate - 6strawberies
	
	
	# data.plot(subplots = True, figsize = (10,10))
	import pandas as pd
	df = data.diff().dropna()
	# Extracting X and Y values as numpy arrays
	X = df[['ROSES', 'CHOCOLATE', 'STRAWBERRIES']].values
	Y = df['GIFT_BASKET'].values
	
	# Adding a column of ones to X for the intercept term
	
	
	# Calculating parameters using numpy's linear algebra module
	parameters = np.linalg.inv(X.T.dot(X)).dot(X.T).dot(Y)
	
	# Extracting intercept and coefficients
	
	print(f"Parameters: {parameters}")
	
	
	# Extracting coefficients
	coefficients = parameters
	
	# Number of observations
	n = X.shape[0]
	
	# Degrees of freedom
	df = n - X.shape[1]
	
	# Residuals
	residuals = Y - X.dot(parameters)
	
	# Residual sum of squares
	RSS = np.sum(residuals ** 2)
	
	# Sample variance of the residuals
	sample_var = RSS / df
	
	# Variance-covariance matrix of coefficients
	var_cov_matrix = np.linalg.inv(X.T.dot(X)) * sample_var
	
	# Standard errors of coefficients (square root of diagonal elements of var_cov_matrix)
	standard_errors = np.sqrt(np.diag(var_cov_matrix))
	
	# t-value for a 95% confidence interval (two-tailed test)
	t_value = 2.262  # For a two-tailed test with 95% confidence and df = n - p (p is the number of predictors)
	
	# Confidence intervals for coefficients
	conf_intervals = [(parameters[i] - t_value * standard_errors[i], parameters[i] + t_value * standard_errors[i]) for i in range(X.shape[1])]
	
	print("Coefficients:", coefficients)
	print("Confidence Intervals for Coefficients:")
	for i in range(X.shape[1]):
	    print("Coefficient {}: {:.4f} - {:.4f}".format(i+1, conf_intervals[i][0], conf_intervals[i][1]))
