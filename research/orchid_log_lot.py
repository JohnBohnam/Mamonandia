import matplotlib.pyplot as plt
import pandas as pd

pd.set_option('display.max_columns', None)
pd.set_option('display.width', None)
pd.set_option('display.max_rows', None)
humidity_thresholds = [60, 80]
sunlight_thresholds = [2500]
folder = "logs_data/"
str_dict = pd.read_csv(folder + "sandbox_logs.csv", sep = ";")["lambdaLog"].values
#eval string into dict
dicts = [eval(x) for x in str_dict]
plot_df = pd.DataFrame(dicts).set_index("time")
plot_df["importTariff"] = plot_df["importTariff"]*(-1)
plot_df["bidPrice"] = plot_df["bidPrice"] - plot_df["transportFees"] - plot_df["exportTariff"]
plot_df["askPrice"] = plot_df["askPrice"] + plot_df["transportFees"] - plot_df["importTariff"]
# plot_df.columns ['best_bid', 'best_ask', 'bidPrice', 'askPrice', 'transportFees',
#        'exportTariff', 'importTariff', 'sunlight', 'humidity'],
n_plots = 4
selected_cols1 = ['best_bid', 'best_ask', 'bidPrice', 'askPrice']
selected_cols2 = ["transportFees", "exportTariff", "importTariff"]
selected_cols3 = ["sunlight"]
selected_cols4 = ["humidity"]
selected_cols_list = [selected_cols1, selected_cols2, selected_cols3, selected_cols4]
fig, axs = plt.subplots(n_plots, 1, sharex = True)
for selected_cols, ax in zip(selected_cols_list, axs):
	plot_df[selected_cols].plot(ax = ax)

#humidity_thresholds  plot on ax[2]
for threshold in humidity_thresholds:
	axs[3].axhline(y = threshold, color = "r")

#sunlight_thresholds  plot on ax[3]
for threshold in sunlight_thresholds:
	axs[2].axhline(y = threshold, color = "r")

days = [-1,0,1]
folder = "backtest/new_data/"
data = []

for day in days:
	file_name = f"prices_round_2_day_{day}.csv"
	data.append(pd.read_csv(folder + file_name, sep = ";"))
	
day = 1
plot_df = data[day].set_index("timestamp")
plot_df["IMPORT_TARIFF"] = plot_df["IMPORT_TARIFF"]*(-1)
# columns 'timestamp', 'ORCHIDS', 'TRANSPORT_FEES', 'EXPORT_TARIFF',
#        'IMPORT_TARIFF', 'SUNLIGHT', 'HUMIDITY', 'DAY'
selected_cols1 = ['ORCHIDS']
selected_cols2 = ["TRANSPORT_FEES", "EXPORT_TARIFF", "IMPORT_TARIFF"]
selected_cols3 = ["SUNLIGHT"]
selected_cols4 = ["HUMIDITY"]
selected_cols_list = [selected_cols1, selected_cols2, selected_cols3, selected_cols4]
fig, axs = plt.subplots(n_plots, 1, sharex = True)
for selected_cols, ax in zip(selected_cols_list, axs):
	plot_df[selected_cols].plot(ax = ax)
#humidity_thresholds  plot on ax[2]
for threshold in humidity_thresholds:
	axs[3].axhline(y = threshold, color = "r")

#sunlight_thresholds  plot on ax[3]
for threshold in sunlight_thresholds:
	axs[2].axhline(y = threshold, color = "r")

