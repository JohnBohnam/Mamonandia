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
	
	def __init__(self, verbose = False):
		self.limit_hits_up = {}
		self.limit_hits_down = {}
		self.limits = {}
		self.runs = 0
		
		self.verbose = verbose
		self.products = ["STARFRUIT", "AMETHYSTS", "ORCHIDS", 'GIFT_BASKET', 'ROSES', 'CHOCOLATE',
		                 'STRAWBERRIES']
		
		for product in self.products:
			self.limit_hits_up[product] = 0
			self.limit_hits_down[product] = 0
			self.limits[product] = 20
		
		self.limits["ORCHIDS"] = 100
		# round 3
		self.basket_std = 76
		self.limits.update({"ROSES": 60, "CHOCOLATE": 250, "STRAWBERRIES": 350, "GIFT_BASKET": 60})
		self.basket_half_spread = 5
		self.cont_buy_basket_unfill = 0
		self.cont_sell_basket_unfill = 0
		# self.coefs = {"ROSES": 1, "CHOCOLATE": 4, "STRAWBERRIES": 5}
		#
		
		print("Trader initialized with params: ", self.__dict__)
	
	def run(self, state: TradingState):
		result = {
				"ORCHIDS"  : self.order_orchid(state),
				"STARFRUIT": self.order_starfruit(state),
				"AMEHTYSTS": self.order_amethysts(state),
		}
		result.update(self.order_gift_basket(state))
		self.run_routine(state)
		
		# conversions here (2nd tuple element)
		return result, 0, ""
	
	def run_routine(self, state: TradingState):
		self.update_limit_hits(state)
		self.runs += 1
		if self.verbose:
			print(f"Run {self.runs}")
			print(f"Position: {state.position}")
			print(f"Limit hits up: {self.limit_hits_up}")
			print(f"Limit hits down: {self.limit_hits_down}")
	
	def order_amethysts(self, state: TradingState):
		orders = []
		# ...
		return orders
	
	def order_starfruit(self, state: TradingState):
		orders = []
		# ...
		return orders
	
	def order_orchid(self, state: TradingState):
		orders = []
		# ...
		return orders
	
	def update_limit_hits(self, state: TradingState):
		for product in self.products:
			if product in state.position and state.position[product] == self.limits[product]:
				self.limit_hits_up[product] += 1
			elif product in state.position and state.position[product] == -self.limits[product]:
				self.limit_hits_down[product] += 1
		return self.limit_hits_up, self.limit_hits_down
	
	def order_gift_basket(self, state):
		
		orders = {"GIFT_BASKET": [], "ROSES": [], "CHOCOLATE": [], "STRAWBERRIES": []}
		prods = ['ROSES', 'CHOCOLATE', 'STRAWBERRIES', 'GIFT_BASKET']
		osell, obuy, best_sell, best_buy, worst_sell, worst_buy, mid_price, vol_buy, vol_sell = {}, {}, {}, {}, {}, {}, {}, {}, {}
		
		for p in prods:
			osell[p] = state.order_depths[p].sell_orders
			obuy[p] = state.order_depths[p].buy_orders
			
			best_sell[p] = min(state.order_depths[p].sell_orders)
			best_buy[p] = max(state.order_depths[p].buy_orders)
			
			worst_sell[p] = max(state.order_depths[p].sell_orders)
			worst_buy[p] = min(state.order_depths[p].buy_orders)
			
			mid_price[p] = (best_sell[p] + best_buy[p]) / 2
		
		res_buy = mid_price['GIFT_BASKET'] - mid_price['ROSES'] - mid_price['CHOCOLATE'] * 4 - \
		          mid_price['STRAWBERRIES'] * 6 - 390
		res_sell = mid_price['GIFT_BASKET'] - mid_price['ROSES'] - mid_price['CHOCOLATE'] * 4 - \
		           mid_price['STRAWBERRIES'] * 6 - 390
		
		trade_at = self.basket_std * 0.5
		
		traded_product = "GIFT_BASKET"
		pb_pos = state.position.get(traded_product, 0)
		pb_neg = state.position.get(traded_product, 0)
		pos = state.position.get(traded_product, 0)
		lim = self.limits[traded_product]
		
		print(state.position)
		if res_sell > trade_at:
			vol = pos + lim
			self.cont_buy_basket_unfill = 0  # no need to buy rn
			assert (vol >= 0)
			if vol > 0:
				orders[traded_product].append(
						Order(traded_product, worst_buy[traded_product], -vol))
				pb_neg -= vol
		# uku_pos += vol
		elif res_buy < -trade_at:
			vol = lim - pos
			assert (vol >= 0)
			if vol > 0:
				orders[traded_product].append(
						Order(traded_product, worst_sell[traded_product], vol))
				self.cont_buy_basket_unfill += 2
				pb_pos += vol
		for traded_product in ["ROSES", "CHOCOLATE", "STRAWBERRIES"]:
			pb_pos = state.position.get(traded_product, 0)
			pb_neg = state.position.get(traded_product, 0)
			pos = state.position.get(traded_product, 0)
			lim = self.limits[traded_product]
			spread = best_sell[traded_product] - best_buy[traded_product]
			
			if res_sell > trade_at and spread <= 1.0:
				vol = pos + lim
				self.cont_buy_basket_unfill = 0  # no need to buy rn
				assert (vol >= 0)
				if vol > 0:
					orders[traded_product].append(
							Order(traded_product, best_buy[traded_product], -vol))
					pb_neg -= vol
			# uku_pos += vol
			elif res_buy < -trade_at and spread <= 1.0:
				vol = lim - pos
				assert (vol >= 0)
				if vol > 0:
					orders[traded_product].append(
							Order(traded_product, best_sell[traded_product], vol))
					self.cont_buy_basket_unfill += 2
					pb_pos += vol
		
		return orders
	
	def order_roses(self, state):
		orders = []
		
		return orders
	
	def order_chocolate(self, state):
		orders = []
		
		return orders
	
	def order_strawberries(self, state):
		orders = []
		
		return orders




