import matplotlib.pyplot as plt
class Plotter:
	'''
	prepare stats based on the states, trader, profits_by_symbol, balance_by_symbol
	the stats_dict is of the form {title: (x, {label: y})} OR {title: (x, y)}
	'''
	def __init__(self, symbols,  states, trader, profits_by_symbol, balance_by_symbol):
		'''
		:param symbols: [str]
		:param states: dict[timestamp, TradingState]
		:param trader: Trader
		:param profits_by_symbol:dict[timestamp, dict[symbol, value]]
		:param balance_by_symbol: dict[timestamp, dict[symbol, potential_profit]]
		'''
		self.symbols = symbols
		self.states = states
		self.trader = trader
		self.profits_by_symbol = profits_by_symbol
		self.balance_by_symbol = balance_by_symbol
		self.stats_dict = {
				"Profit by symbol"  : self.get_profits_per_product(),
				"Exposure by symbol": self.get_balance_per_product(),
				"Position by symbol": self.get_position_per_product(),
		}
		
	def get_profits_per_product(self):
		profits_by_symbol = self.profits_by_symbol
		result = {}
		for symbol in self.symbols:
			timestamps = profits_by_symbol.keys()
			profits = [profits_by_symbol[ts][symbol] for ts in timestamps]
			result[symbol] = profits
		return (timestamps, result)
	
	def get_balance_per_product(self):
		balance_by_symbol = self.balance_by_symbol
		result = {}
		for symbol in self.symbols:
			timestamps = balance_by_symbol.keys()
			balances = [balance_by_symbol[ts][symbol] for ts in timestamps]
			result[symbol] = balances
		return (timestamps, result)
	
	def get_position_per_product(self):
		states = self.states
		result = {}
		for symbol in self.symbols:
			timestamps = states.keys()
			positions = [states[ts].position[symbol] for ts in timestamps]
			result[symbol] = positions
		return (timestamps, result)
	
	
	
	
	
	# dict for the plot, key is title, value is a function that can take any of states, trader, profits_by_symbol, balance_by_symbol
	
	def plot_stats(self):
		num_plots = len(self.stats_dict)
		fig, axes = plt.subplots(1, num_plots, figsize = (6 * num_plots, 6))
		
		for i, (title, stats) in enumerate(self.stats_dict.items()):
			ax = axes[i]
			if type(stats[1]) != dict:
				x, y = stats
				ax.plot(x, y)
			else:
				x = stats[0]
				for label, y in stats[1].items():
					ax.plot(x, y, label = label)
			ax.set_title(title)
			ax.legend()
		
		plt.tight_layout()
		plt.show()