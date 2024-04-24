from datamodel import TradingState, Order
import numpy as np


def calculate_buy_quantity(order_depth, target_price):
	asks = order_depth.sell_orders
	q = sum([-y for x, y in asks.items() if x <= target_price])
	return q


def calculate_sell_quantity(order_depth, target_price):
	bids = order_depth.buy_orders
	q = sum([-y for x, y in bids.items() if x >= target_price])
	return q


class Trader:

	def __init__(self, verbose=False):
		self.limit_hits_up = {}
		self.limit_hits_down = {}
		self.limits = {}
		self.runs = 0

		self.verbose = verbose
		self.products = ["STARFRUIT", "AMETHYSTS", "ORCHIDS", "COCONUT", "COCONUT_COUPON"]
		self.coconut_window = 100

		for product in self.products:
			self.limit_hits_up[product] = 0
			self.limit_hits_down[product] = 0
			self.limits[product] = 20

		self.limits["ORCHIDS"] = 100
		self.limits["COCONUT"] = 300
		self.limits["COCONUT_COUPON"] = 600
		self.coconut_window = 1000
		self.coconut_spread_history = []
		self.coconut_prev_mids = {"COCONUT": None, "COCONUT_COUPON": None}
		self.coconut_multipliers = {"COCONUT": -1, "COCONUT_COUPON": 2}
		self.coconut_spread_limit = 30
		self.target_n_spreads = 0
		

		print("Trader initialized with params: ", self.__dict__)

	def run(self, state: TradingState):
		pos = state.position
		result = self.order_spread(state)
		# self.run_routine(state)

		# conversions here (2nd tuple element)
		return result, 0, ""


	def order_spread(self, state: TradingState):
		
		orders = {"COCONUT":[], "COCONUT_COUPON":[]}
		mids = {}
		for product in ["COCONUT", "COCONUT_COUPON"]:
			if len(state.order_depths[product].buy_orders) == 0 or len(state.order_depths[product].sell_orders) == 0:
				return orders
			best_bid = max(state.order_depths[product].buy_orders.keys())
			best_ask = min(state.order_depths[product].sell_orders.keys())
			mids[product] = (best_bid + best_ask) / 2
		
		# get mids diff
		# diff = {}
		# for product in ["COCONUT", "COCONUT_COUPON"]:
		# 	if self.coconut_prev_mids[product] is None:
		# 		self.coconut_prev_mids[product] = mids[product]
		# 		return orders
		# 	else:
		# 		diff[product] = mids[product] - self.coconut_prev_mids[product]
		# 		self.coconut_prev_mids[product] = mids[product]
		# spread = self.coconut_multipliers["COCONUT"] * diff["COCONUT"] + self.coconut_multipliers["COCONUT_COUPON"] * diff["COCONUT_COUPON"]
		spread = mids["COCONUT_COUPON"]*self.coconut_multipliers["COCONUT_COUPON"] + mids["COCONUT"]*self.coconut_multipliers["COCONUT"]
		self.coconut_spread_history.append(spread)
		self.coconut_spread_history = self.coconut_spread_history[-self.coconut_window:]
		if len(self.coconut_spread_history) < self.coconut_window*0.5:
			return orders
		
		spread_value = spread - np.median(self.coconut_spread_history)
		if abs(spread_value) > self.coconut_spread_limit:
			print(f"Spread value: {spread_value} for time {state.timestamp}")
		
		if state.timestamp==245000:
			print(f"Spread value: {spread_value} for time {state.timestamp}")
		current_n_spreads = state.position.get("COCONUT_COUPON", 0)/self.coconut_multipliers["COCONUT_COUPON"]
		if spread_value>self.coconut_spread_limit:
			self.target_n_spreads = -self.limits["COCONUT_COUPON"]/self.coconut_multipliers["COCONUT_COUPON"]
		elif spread_value< -self.coconut_spread_limit:
			self.target_n_spreads = int(self.limits["COCONUT_COUPON"]/self.coconut_multipliers["COCONUT_COUPON"])
		elif current_n_spreads*spread_value>0:
			self.target_n_spreads = 0
		else:
			return orders
		
		target_n_spreads = self.target_n_spreads
		print(f"Current n_spreads: {current_n_spreads}, target n_spreads: {target_n_spreads}")
		
		if target_n_spreads<current_n_spreads:
			worst_bid_coupon = min(state.order_depths["COCONUT_COUPON"].buy_orders.keys())
			worst_ask_coconut = max(state.order_depths["COCONUT"].sell_orders.keys())
			# quantity to sell coupon
			q_coupon = calculate_sell_quantity(state.order_depths["COCONUT_COUPON"], worst_bid_coupon)
			q_coupon = max(q_coupon, self.coconut_multipliers["COCONUT_COUPON"]*(target_n_spreads - current_n_spreads))
			# quantity to buy coconut
			q_coconut = calculate_buy_quantity(state.order_depths["COCONUT"], worst_ask_coconut)
			q_coconut = min(q_coconut, (target_n_spreads - current_n_spreads)*self.coconut_multipliers["COCONUT"])
			n_spreads = -min(abs(q_coupon/self.coconut_multipliers["COCONUT_COUPON"]), abs(q_coconut/self.coconut_multipliers["COCONUT"]))
			# q_coconut = int(n_spreads*self.coconut_multipliers["COCONUT"])
			q_coconut = int((current_n_spreads + n_spreads)*self.coconut_multipliers["COCONUT"] - state.position.get("COCONUT", 0))
			q_coupon = int(n_spreads*self.coconut_multipliers["COCONUT_COUPON"])
			orders["COCONUT_COUPON"].append(Order("COCONUT_COUPON", worst_bid_coupon, q_coupon))
			orders["COCONUT"].append(Order("COCONUT", worst_ask_coconut, q_coconut))
		elif target_n_spreads>current_n_spreads:
			worst_ask_coupon = max(state.order_depths["COCONUT_COUPON"].sell_orders.keys())
			worst_bid_coconut = min(state.order_depths["COCONUT"].buy_orders.keys())
			# quantity to buy coupon
			q_coupon = calculate_buy_quantity(state.order_depths["COCONUT_COUPON"], worst_ask_coupon)
			q_coupon = min(q_coupon, self.coconut_multipliers["COCONUT_COUPON"]*(target_n_spreads - current_n_spreads))
			# quantity to sell coconut
			q_coconut = calculate_sell_quantity(state.order_depths["COCONUT"], worst_bid_coconut)
			q_coconut = max(q_coconut, (target_n_spreads - current_n_spreads)*self.coconut_multipliers["COCONUT"])
			n_spreads = min(abs(q_coupon/self.coconut_multipliers["COCONUT_COUPON"]), abs(q_coconut/self.coconut_multipliers["COCONUT"]))
			# q_coconut = int(n_spreads*self.coconut_multipliers["COCONUT"])
			q_coconut = int((current_n_spreads + n_spreads) * self.coconut_multipliers[
				"COCONUT"] - state.position.get("COCONUT", 0))
			q_coupon = int(n_spreads*self.coconut_multipliers["COCONUT_COUPON"])
			orders["COCONUT_COUPON"].append(Order("COCONUT_COUPON", worst_ask_coupon, q_coupon))
			orders["COCONUT"].append(Order("COCONUT", worst_bid_coconut, q_coconut))
			
		return orders


	def run_routine(self, state: TradingState):
		self.update_limit_hits(state)
		self.runs += 1
		if self.verbose:
			print(f"Run {self.runs}")
			print(f"Position: {state.position}")
			print(f"Limit hits up: {self.limit_hits_up}")
			print(f"Limit hits down: {self.limit_hits_down}")

	def update_limit_hits(self, state: TradingState):
		for product in self.products:
			if product in state.position and state.position[product] == self.limits[product]:
				self.limit_hits_up[product] += 1
			elif product in state.position and state.position[product] == -self.limits[product]:
				self.limit_hits_down[product] += 1
		return self.limit_hits_up, self.limit_hits_down
