from typing import List

from datamodel import OrderDepth, TradingState, Order, Time
import numpy as np
class Trader:

	def __init__(self, sell_margin=1, buy_margin=1, time_window=2, verbose=False):
		self.limit_hits_up = {}
		self.limit_hits_down = {}
		self.limits = {}
		self.runs = 0

		self.prev_mids = []
		self.buy_margin = sell_margin
		self.sell_margin = buy_margin
		self.time_window = time_window

		self.verbose = verbose

		self.products = ["STARFRUIT", "AMETHYSTS"]
		self.history_stairfruit:List[(Time, OrderDepth)] = []
		self.history_size = 20

		for product in self.products:
			self.limit_hits_up[product] = 0
			self.limit_hits_down[product] = 0
			self.limits[product] = 20
	
	def merge_dicts(self, list_of_dicts):
		merged_dict = {}
		for d in list_of_dicts:
			for key, value in d.items():
				if key in merged_dict:
					merged_dict[key] += value
				else:
					merged_dict[key] = value
		return merged_dict
	
	def get_historical_trades_for_stairfruit(self):
		result = [x[1] for x in self.history_stairfruit]
		return {"buy_orders": self.merge_dicts([x.buy_orders for x in result]), "sell_orders": self.merge_dicts([x.sell_orders for x in result])}

	




	def run(self, state: TradingState):
		self.runs += 1
		# print(f"limits up: {self.limit_hits_up}, limits down: {self.limit_hits_down}\n")
		# print(f"runs: {self.runs}\n")
		position = state.position
		self.history_stairfruit.append((state.timestamp, state.order_depths["STARFRUIT"]))
		self.history_stairfruit = self.history_stairfruit[-self.history_size:]
		r1= self.get_historical_trades_for_stairfruit()
		print(r1)
		for product in self.products:
			if product in position and position[product] == self.limits[product]:
				self.limit_hits_up[product] += 1
			elif product in position and position[product] == -self.limits[product]:
				self.limit_hits_down[product] += 1

		result = {"STARFRUIT": [], "AMETHYSTS": []}


		return result, 0, ""
