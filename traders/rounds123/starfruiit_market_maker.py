from typing import List, Dict
import numpy as np
from datamodel import OrderDepth, TradingState, Order, Time

class Trader:

	def __init__(self, verbose=False):
		self.spread = 5
		self.verbose = verbose
		self.single_position_limit = 7
		
	

	def run(self, state: TradingState):



		result = {"STARFRUIT": [], "AMETHYSTS": []}

		pos = state.position["STARFRUIT"] if "STARFRUIT" in state.position else 0
		best_bid = max(state.order_depths["STARFRUIT"].buy_orders.keys()) if state.order_depths["STARFRUIT"].buy_orders else 0
		best_ask = min(state.order_depths["STARFRUIT"].sell_orders.keys()) if state.order_depths["STARFRUIT"].sell_orders else 0
		spread = best_ask - best_bid
		if spread>self.spread:
			mid = (best_ask + best_bid) / 2 - pos/10
			sell_for = int(np.round(mid + self.spread/2))
			q = -self.single_position_limit
			q = max(q, -20 - pos)
			result["STARFRUIT"].append(Order("STARFRUIT", sell_for, q))


			buy_for = int(round(mid - self.spread/2))
			q = self.single_position_limit
			q = min(q, 20 - pos)
			result["STARFRUIT"].append(Order("STARFRUIT", buy_for, q))
			print(f"time: {state.timestamp}, pos: {pos}")


		return result, 0, ""
