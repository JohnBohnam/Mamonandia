import os.path

import pandas as pd
import matplotlib.pyplot as plt
pd.set_option('display.max_columns', None)


def parse_multiline_json(lines):
	result = []
	block = None
	for line in lines:
		if line.startswith("{"):
			block = [line]
		elif not line.startswith("}") and block is not None:
			block.append(line)
		elif line.startswith("}"):
			block.append(line.replace(",", ""))
			result.append(eval("".join(block)))
			block = None
	return result


def split_log_categories(filename):
	"""
	Splits log entries from a file into three categories based on section headers, excluding empty lines.
 
	Args:
		filename (str): The path to the log file.
  
	Returns:
		tuple: A tuple containing three lists corresponding to:
			- sandbox_logs: List of non-empty lines belonging to the "Sandbox logs:" section.
			- activities_logs: List of non-empty lines belonging to the "Activities log:" section.
			- trade_history_logs: List of non-empty lines belonging to the "Trade History:" section.
	"""
	
	with open(filename, 'r') as f:
		lines = f.readlines()
	
	sandbox_logs = []
	activities_logs = []
	trade_history_logs = []
	current_section = None
	
	for line in lines:
		line = line.strip()  # Remove leading/trailing whitespace
		if not line:  # Skip empty lines
			continue
		
		if line.startswith('Sandbox logs:'):
			current_section = 'sandbox'
		elif line.startswith('Activities log:'):
			current_section = 'activities'
		elif line.startswith('Trade History:'):
			current_section = 'trade_history'
		else:
			if current_section:  # Add non-empty line to the appropriate category
				if current_section == 'sandbox':
					sandbox_logs.append(line)
				elif current_section == 'activities':
					activities_logs.append(line)
				elif current_section == 'trade_history':
					trade_history_logs.append(line)
	
	return sandbox_logs, activities_logs, trade_history_logs


# Example usage (replace 'logs.txt' with your actual filename)
folder = 'backtest/logs'
output_folder = "logs_data/"

checker = []
result = {}
for spread in range(1, 5):
	
	file_name = f"orchid50_spread_{spread}.log"
	# file_name = "orchid50_mm_spread.log"
	sandbox_logs, _, trade_history_logs = split_log_categories(	os.path.join(folder, file_name))
	
	sandbox_logs_df = pd.DataFrame(parse_multiline_json(sandbox_logs))
	str_dict = sandbox_logs_df["lambdaLog"].values
	#eval string into dict
	dicts = [eval(x.split("\n")[0]) for x in str_dict[:1000]]
	sandbox_logs_df = pd.DataFrame(dicts)
	trade_history_df = pd.DataFrame(parse_multiline_json(trade_history_logs))
	trade_history_df = trade_history_df[trade_history_df["symbol"] == "ORCHIDS"]
	good_timestamps = trade_history_df[trade_history_df["quantity"]>25]["timestamp"].values
	sandbox_logs_df.head()
	sandbox_logs_df["mm_happened"] = sandbox_logs_df["time"].apply(lambda x: x in good_timestamps)*1.0
	
	s1 = sandbox_logs_df["mm_happened"].rolling(20).mean().values
	result[spread] = s1
	
for y, label in result.items():
	plt.plot(label, label = f"spread {y}")
plt.legend()