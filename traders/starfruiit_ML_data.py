from typing import List, Dict
import numpy as np
from datamodel import OrderDepth, TradingState, Order, Time

class Trader:

	def __init__(self, verbose=False):
		self.spread = 5
		self.verbose = verbose
		self.single_position_limit = 7
		self.prev_bid_1 = []
		self.prev_bid_volume_1=[]
		self.prev_bid_volume_2 = []
		self.prev_ask_1 = []
		self.prev_ask_volume_1 = []
		self.prev_ask_volume_2 = []
		self.hist_len=5

#colls_taken = ['bid_price_1', 'bid_volume_1', 'ask_price_1', 'ask_volume_1', 'bid_volume_2', 'ask_volume_2']

		#X = []

	def update_prevs(self, product, state: TradingState):
		if product not in state.order_depths:
			return
		od = state.order_depths[product]

		bid_price = None
		bid_price_2=None

		if od.buy_orders:
			bid_price = max(od.buy_orders.keys())
			bid_vol_1=od.buy_orders[bid_price]
			if(len(od.buy_orders.keys())>1):
				bid_price_2=min(od.buy_orders.keys())
				bid_vol_2 = od.buy_orders[bid_price_2]
			else:
				bid_vol_2=0
			#od.buy_orders.keys())
		elif self.prev_bid_1:
			bid_price = self.prev_bid_1[-1]
			bid_vol_1=0
			bid_vol_2 = 0
		# print("no bids, using prev")

		if bid_price is not None:
			#if(len(self.prev_bid_1)=5):
			self.prev_bids.append(bid_price)
			self.prev_bids = self.prev_bid_1[-self.hist_len:]
			#self.prev_bid_volume_1 = self.prev_bid_volume_1[1:]  # drops first element
			self.prev_bid_volume_1.append(bid_vol_1)
			self.prev_bid_volume_1 = self.prev_bid_volume_1[-self.hist_len:]  # drops first element
			self.prev_bid_volume_2.append(bid_vol_2)
			self.prev_bid_volume_2 = self.prev_bid_volume_2[-self.hist_len:]  # drops first element



		ask_price = None
		ask_price_2=None
		if od.sell_orders:
			ask_price = min(od.sell_orders.keys())
			ask_vol_1 = od.sell_orders[ask_price]
			if (len(od.sell_orders.keys()) > 1):
				ask_price_2 = max(od.sell_orders.keys())
				ask_vol_2 = od.sell_orders[ask_price_2]
			else:
				ask_vol_2 = 0
		elif self.prev_ask_1:
			ask_price = self.prev_ask_1[-1]
			ask_vol_1=0
			ask_vol_2 = 0
		# print("no bids, using prev")

		if ask_price is not None:

			self.prev_ask_1.append(ask_price)
			self.prev_ask_1 = self.prev_ask_1[-self.hist_len:]  # drops first element
			self.prev_ask_volume_1.append(ask_vol_1)
			self.prev_ask_volume_1 = self.prev_ask_volume_1[-self.hist_len:]  # drops first element
			self.prev_ask_volume_2.append(bid_vol_2)
			self.prev_ask_volume_2 = self.prev_ask_volume_2[-self.hist_len:]  # drops first element


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


