from typing import Dict, List

from research.datamodel import OrderDepth, TradingState, Order

from traders.dontlooseshells_algo import Logger


class Trader:
	
	acceptable_price = {"PEARLS": None, "BANANAS": None, "COCONUTS": None, "PINA_COLADAS": None}
	spread = {"PEARLS": 0.570152, "BANANAS": 0.7690351939420956, "PCC": 1.0}
	limits = {"PEARLS": 20, "BANANAS": 20, "PINA_COLADAS": 300, "COCONUTS": 600}
	reverse_multiplier = {
			"PEARLS" : 0.4374207359283349,
			"BANANAS": 0.7634221935718115,
			"PCC"    : 0.8841777102972426
	}
	alpha = {
			"PEARLS"      : 0.86547,
			"BANANAS"     : 0.01222034273191291,
			"PINA_COLADAS": 0.0,
			"COCONUTS"    : 0.0
	}
	weights = {"PEARLS": 0.033808, "BANANAS": 0.4524093452839253, "PCC": 1.0}
	regression = {"BANANAS": -0.5296188741893867, "PEARLS": 0.010117, "PCC": -0.2}
	yesterday_price = {"PEARLS": None, "BANANAS": None, "COCONUTS": None, "PINA_COLADAS": None}
	mid_price = {"PEARLS": None, "BANANAS": None, "COCONUTS": 8000, "PINA_COLADAS": 15000}
	prev_position = {}
	prev_market_trades = {}
	prev_own_trades = {}
	acceptable_price_empty = True
	checked_product = ""
	PCC_m = -0.33
	logger = Logger(local=True)
	
	def __init__(self):
		# self.spread = spread
		# self.reverse_multiplier = rev_mult
		# self.regression = regression
		# self.checked_product = product
		# self.weights = weights
		# self.alpha = alpha
		# if product in {"COCONUTS", "PINA_COLADAS"}:
		# 	self.checked_product = {"COCONUTS", "PINA_COLADAS"}
		#
	    return
	
	def run(self, state: TradingState) -> Dict[str, List[Order]]:
		"""
		Only method required. It takes all buy and sell orders for all symbols as an input,
		and outputs a list of orders to be sent
		"""
		# initial acceptable price
		if self.acceptable_price_empty:
			self.init_acceptable_price(state)
		# Initialize the method output dict as an empty dict
		# result = {}
		
		# print("timestamp")
		# self.initial_logs(state)
		
		# Iterate over all the keys (the available products) contained in the order dephts
		
		result = self.bot1(state, update_acceptable_price_f = self.update_acceptable_price)
		self.logger.flush(state, result)
		return result
	
	def update_acceptable_price(self, state):
		
		for product in state.order_depths.keys():
			acceptable_price = self.acceptable_price[product]
			limit = self.limits[product]
			order_depth: OrderDepth = state.order_depths[product]
			best_bid = max(order_depth.buy_orders.keys())
			best_ask = min(order_depth.sell_orders.keys())
			current_pos = state.position.get(product, 0)
			if current_pos > (0.75 * limit) and acceptable_price > best_ask:
				acceptable_price = best_ask
				print("acceptable price been updated:", self.acceptable_price)
			if current_pos < (-0.75 * limit) and acceptable_price < best_bid:
				acceptable_price = best_bid
				print("acceptable price been updated:", self.acceptable_price)
			self.acceptable_price[product] = acceptable_price
		return
	
	def update_acceptable_price2(self, state):
		
		for product in state.order_depths.keys():
			acceptable_price = self.acceptable_price[product]
			order_depth: OrderDepth = state.order_depths[product]
			alpha = self.alpha.get(product, 0)
			try:
				best_bid = max(order_depth.buy_orders.keys())
				best_ask = min(order_depth.sell_orders.keys())
				fair_price = (best_bid + best_ask) / 2
				self.acceptable_price[product] = alpha * fair_price + (1 - alpha) * acceptable_price
			except ValueError:
				continue
		return
	
	def update_acceptable_price3(self, state):
		
		for product in state.order_depths.keys():
			acceptable_price = self.acceptable_price[product]
			order_depth: OrderDepth = state.order_depths[product]
			alpha = self.alpha[product]
			try:
				best_bid = max(order_depth.buy_orders.keys())
				bid_q = order_depth.buy_orders[best_bid]
				best_ask = min(order_depth.sell_orders.keys())
				ask_q = -order_depth.sell_orders[best_ask]
				# (best_bid * ask_q + best_ask * bid_q / (bid_q+ask_q)
				fair_price = (best_bid * ask_q + best_ask * bid_q) / (bid_q + ask_q)
				self.acceptable_price[product] = alpha * fair_price + (1 - alpha) * acceptable_price
			except Exception as e:
				continue
		return
	
	def initial_logs(self, state):
		if state.position != self.prev_position:
			print("my position:", state.position)
			self.prev_position = state.position
		
		if not self.equal_trades(self.prev_own_trades, state.own_trades):
			print("own trades:", state.own_trades)
			self.prev_own_trades = state.own_trades
		if not self.equal_trades(self.prev_market_trades, state.market_trades):
			print("market trades:", state.market_trades)
			self.prev_market_trades = state.market_trades
	
	def equal_trades(self, inp1, inp2):
		if inp1.keys() != inp2.keys():
			return False
		for key in inp1.keys():
			if str(inp1[key]) != str(inp2[key]):
				return False
		return True
	
	def bot1(self, state, update_acceptable_price_f, **kwargs):
		result = {}
		self.update_mid_price(state)
		for product in state.order_depths.keys():
			if product not in self.checked_product:
				continue
			
			# Check if the current product is the 'PEARLS' product, only then run the order logic
			
			# Retrieve the Order Depth containing all the market BUY and SELL orders for PEARLS
			order_depth: OrderDepth = state.order_depths[product]
			
			# Initialize the list of Orders to be sent as an empty list
			orders: list[Order] = []
			# print(product, "market buy orders ", order_depth.buy_orders)
			# print(product, "market sell orders ", order_depth.sell_orders)
			# Define a fair value for the PEARLS.
			# Note that this value of 1 is just a dummy value, you should likely change it!
			current_pos = state.position.get(product, 0)
			if product == "COCONUT":
				current_pos += self.PCC_m * state.position.get("PINA_COLADAS", 0)
			if product == "PINA_COLADAS":
				current_pos += state.position.get("COCONUTS", 0) / self.PCC_m
			# self.acceptable_price -= current_pos / 15
			mid_price = self.mid_price[product]
			weight = self.weights[product]
			yesterday_price = self.yesterday_price[product]
			tomorrow_change = self.regression[product] * (mid_price - yesterday_price)
			self.yesterday_price[product] = mid_price
			
			acceptable_price = weight * (mid_price + tomorrow_change) + (1 - weight) * \
							   self.acceptable_price[product]
			reverse_multiplier = self.reverse_multiplier[product]
			buy_spread = self.spread[product] + current_pos / (
					reverse_multiplier * self.limits[product])
			sell_spread = self.spread[product] - current_pos / (
					reverse_multiplier * self.limits[product])
			
			buy_price = (acceptable_price - buy_spread) // 1
			buy_volume = -sum([y for x, y in order_depth.sell_orders.items() if
							   x <= (acceptable_price - buy_spread)])
			buy_volume = min(buy_volume, self.limits[product] // 2)
			buy_volume = max(buy_volume, 2)
			buy_volume = min(buy_volume, self.limits[product] - current_pos)
			
			orders.append(Order(product, buy_price, buy_volume))
			
			# The below code block is similar to the one above,
			# the difference is that it find the highest bid (buy order)
			# If the price of the order is higher than the fair value
			# This is an opportunity to sell at a premium
			sell_price = (acceptable_price + sell_spread) // 1
			# if np.isnan(buy_price) or np.isnan(sell_price):
			# 	pdb.set_trace()
			sell_volume = -sum([y for x, y in order_depth.sell_orders.items() if
								x >= sell_price])
			sell_volume = max(sell_volume, -self.limits[product] // 2)
			sell_volume = min(sell_volume, -2)
			sell_volume = max(sell_volume, -self.limits[product] - current_pos)
			orders.append(Order(product, sell_price, sell_volume))
			# print("my orders:",product,":", orders)
			# Add all the above the orders to the result dict
			result[product] = orders
		
		# result.update(self.orders_PCC(state))
		update_acceptable_price_f(state, **kwargs)
		
		# print("my orders:", result)
		# print(product, "market buy orders ", order_depth.buy_orders)
		
		return result
	
	
	def init_acceptable_price(self, state):
		for product in state.order_depths.keys():
			order_depth: OrderDepth = state.order_depths[product]
			try:
				best_bid = max(order_depth.buy_orders.keys())
				best_ask = min(order_depth.sell_orders.keys())
				fair_price = (best_bid + best_ask) / 2
				self.acceptable_price[product] = fair_price
				self.yesterday_price[product] = fair_price
			except ValueError:
				continue
		for acceptable_price in self.acceptable_price.values():
			if acceptable_price is None:
				return
		self.acceptable_price_empty = False
	
	def update_mid_price(self, state):
		for product in state.order_depths.keys():
			order_depth: OrderDepth = state.order_depths[product]
			try:
				best_bid = max(order_depth.buy_orders.keys())
				best_ask = min(order_depth.sell_orders.keys())
				mid_price = (best_bid + best_ask) / 2
				self.mid_price[product] = mid_price
			except ValueError:
				continue





