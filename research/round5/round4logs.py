import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
#set unlimited pandas options
pd.set_option('display.max_columns', None)
pd.set_option('display.max_rows', 1000)
pd.set_option('display.width', 300)

folder = "logs_data/"
files ={"sandbox":"sandbox_final4.csv", "prices":"prices_final4.csv", "trades":"trades_final4.csv"}
logs = {x:pd.read_csv(folder + y, sep = ";") for x,y in files.items()}
logs["sandbox"] = logs["sandbox"].iloc[1:,:]

# orchids analysis
def parse_sandbox(s):
	if s is np.nan:
		return {}
	expected_keys = ['OBSERVATION.askPrice', 'OBSERVATION.importTariff',
	                 'OBSERVATION.transportFees', 'South ask', 'Best bid']
	s2 = [x.split(": ") for x in s.split("\n")]
	s3 = {x[0]:x[1] for x in s2 if x[0] in expected_keys}
	return s3
#{'OBSERVATION.askPrice': '1149.5', 'OBSERVATION.importTariff': '-3.0', 'OBSERVATION.transportFees': '1.1', 'South ask': '1147.6', 'Best bid': '1145'}



list_dicts = [parse_sandbox(s)|{"t":t} for s,t in zip(logs["sandbox"]["lambdaLog"].values, logs["sandbox"]["timestamp"].values)]

sandbox_df = pd.DataFrame(list_dicts)

df = logs["trades"].copy()
df = df[df["symbol"] == "ORCHIDS"]
df = df[(df["buyer"]=="SUBMISSION") | (df["seller"]=="SUBMISSION")]
s1 = df.groupby("timestamp")["price"].count()
tss = s1[s1>1].index.values
df = df[df["timestamp"].isin(tss)].sort_values("timestamp")

sandbox_df["min_ask_price"] = sandbox_df["OBSERVATION.askPrice"].astype(float) + sandbox_df["OBSERVATION.importTariff"].astype(float) + sandbox_df["OBSERVATION.transportFees"].astype(float) + 1.0
sandbox_df["min_ask_price"] = sandbox_df["min_ask_price"].round()
df = df.merge(sandbox_df[["min_ask_price", "t"]], left_on = "timestamp", right_on = "t")
df[df["price"]!=df["min_ask_price"]]

# orchids done

#