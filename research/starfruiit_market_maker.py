from typing import List, Dict

from datamodel import OrderDepth, TradingState, Order, Time

class Trader:

	def __init__(self, verbose=False):
		self.spread = 5
		self.verbose = verbose
		
	

	def run(self, state: TradingState):



		result = {"STARFRUIT": [], "AMETHYSTS": []}

		pos = state.position["STARFRUIT"] if "STARFRUIT" in state.position else 0
		best_bid = max(state.order_depths["STARFRUIT"].buy_orders.keys()) if state.order_depths["STARFRUIT"].buy_orders else 0
		best_ask = min(state.order_depths["STARFRUIT"].sell_orders.keys()) if state.order_depths["STARFRUIT"].sell_orders else 0
		spread = best_ask - best_bid
		if spread>self.spread:
			mid = (best_ask + best_bid) / 2
			sell_for = int(mid + self.spread/2)
			result["STARFRUIT"].append(Order("STARFRUIT", sell_for, -20 - pos))
			if self.verbose:
				print("time", state.timestamp)
				print(f"pos: {pos}, selling {-20 - pos} of STARFRUIT for {sell_for}")

			buy_for = int(mid - self.spread/2)
			result["STARFRUIT"].append(Order("STARFRUIT", buy_for, 20 - pos))
			if self.verbose:
				print("time", state.timestamp)
				print(f"pos: {pos}, buying {20 - pos} of STARFRUIT for {buy_for}")

		return result, 0, ""
