import os.path

import pandas as pd
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
      block.append(line.replace(",",""))
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
if __name__ == '__main__':
  folder = 'backtest/logs/'
  output_folder = "logs_data/"
  
  file_name = "round4_run_log.log"
  sandbox_logs, activities_logs, trade_history_logs = split_log_categories(os.path.join(folder, file_name))
  
  print("Sandbox logs head:")
  sandbox_logs_df = pd.DataFrame(parse_multiline_json(sandbox_logs))
  print(sandbox_logs_df.head())
  sandbox_logs_df.to_csv(os.path.join(output_folder, 'sandbox_logs.csv'), index=False, sep = ';' )
  
  print("\nActivities logs:")
  data_list = [row.split(';') for row in activities_logs[1:]]
  column_names = activities_logs[0].split(';')
  activities_df = pd.DataFrame(data_list, columns=column_names)
  print(activities_df.head())
  activities_df.to_csv(os.path.join(output_folder, 'prices_from_logs.csv'), index=False, sep = ';')
  
  
  print("\nTrade History logs:")
  trade_history_df = pd.DataFrame(parse_multiline_json(trade_history_logs))
  print(trade_history_df.head())
  trade_history_df.to_csv(os.path.join(output_folder, 'trades_from_logs.csv'), index=False, sep = ';')
