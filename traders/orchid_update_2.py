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
	
	def __init__(self, buy_margin = 4, sell_margin = 4, time_window = 2, verbose = True):
		self.limit_hits_up = {}
		self.limit_hits_down = {}
		self.limits = {}
		self.runs = 0
		self.prev_bids = []
		self.prev_asks = []
		self.prev_mids = []
		
		self.target_price = 10000
		self.half_spread = 2
		
		self.time_window = time_window
		self.buy_margin = buy_margin
		self.sell_margin = sell_margin
		
		self.spread = 5
		self.single_position_limit = 5
		
		self.prev_south_ask = None
		self.prev_best_bid = None
		self.orchid_margin = 1.2
		self.orchid_window = 100
		self.orchid_spreads = []
		self.min_bid_margin = 1
		self.basket_std = 76
		
		self.verbose = verbose
		self.products = ["STARFRUIT", "AMETHYSTS", "ORCHIDS", 'GIFT_BASKET', 'ROSES', 'CHOCOLATE',
		                 'STRAWBERRIES']
		
		for product in self.products:
			self.limit_hits_up[product] = 0
			self.limit_hits_down[product] = 0
			self.limits[product] = 20
		
		self.limits["ORCHIDS"] = 100
		self.limits.update({"ROSES": 60, "CHOCOLATE": 250, "STRAWBERRIES": 350, "GIFT_BASKET": 60})
		
		print("Trader initialized with params: ", self.__dict__)
	
	def get_orchid_price(self, south_ask, best_bid, margin):
		return int(south_ask+1.5) + margin
	
	
	def update_orchid_trades(self, state: TradingState):
		if "ORCHIDS" not in state.own_trades:
			return 0
		curr_trades = []
		for trade in state.own_trades["ORCHIDS"]:
			if trade.timestamp == state.timestamp - 100:
				curr_trades.append(trade)
		sells = [trade.price for trade in curr_trades if trade.seller == "SUBMISSION"]
		
		if sells:
			max_sell = max(sells)
			curr_spread = max_sell - self.get_orchid_price(self.prev_south_ask,
			                                               self.prev_best_bid, 0)
		else:
			return 0
		
		self.orchid_spreads.append((state.timestamp, curr_spread))
		
		self.orchid_spreads = [(x, y) for x, y in self.orchid_spreads if
		                       state.timestamp - x < self.orchid_window * 100]
		return curr_spread
	
	def update_prevs(self, product, state: TradingState):
		if product not in state.order_depths:
			return
		od = state.order_depths[product]
		
		bid_price = None
		if od.buy_orders:
			bid_price = min(od.buy_orders.keys())
		elif self.prev_bids:
			bid_price = self.prev_bids[-1]
		# print("no bids, using prev")
		
		if bid_price is not None:
			self.prev_bids.append(bid_price)
		
		ask_price = None
		if od.sell_orders:
			ask_price = max(od.sell_orders.keys())
		elif self.prev_asks:
			ask_price = self.prev_asks[0]
		# print("no asks, using prev")
		
		if ask_price is not None:
			self.prev_asks.append(ask_price)
		
		if len(self.prev_bids) > self.time_window:
			self.prev_bids.pop(0)
		if len(self.prev_asks) > self.time_window:
			self.prev_asks.pop(0)
	
	def order_starfruit(self, state: TradingState) -> list[Order]:
		orders = []
		product = "STARFRUIT"
		if product not in state.order_depths:
			return orders
		
		pos = state.position[product] if product in state.position else 0
		
		sell_margin = self.sell_margin
		buy_margin = self.buy_margin
		
		sell_q = 0
		buy_q = 0
		
		lim = self.limits[product]
		
		ods = state.order_depths[product]
		
		if self.prev_bids:
			sell_for = int(np.min(self.prev_bids) + sell_margin)
			sell_q = calculate_sell_quantity(ods, sell_for)
			sell_q = max(sell_q, -lim - pos)
			orders.append(Order(product, sell_for, sell_q))
			if self.verbose:
				print(f"pos: {pos}, selling {sell_q} of {product} for {sell_for}")
		
		if self.prev_asks:
			buy_for = int(np.max(self.prev_asks) - buy_margin)
			buy_q = calculate_buy_quantity(ods, buy_for)
			buy_q = min(buy_q, lim - pos)
			orders.append(Order(product, buy_for, buy_q))
			if self.verbose:
				print(f"pos: {pos}, buying {buy_q} of {product} for {buy_for}")
		
		best_bid = max(ods.buy_orders.keys()) if ods.buy_orders else 0
		best_ask = min(ods.sell_orders.keys()) if ods.sell_orders else 0
		spread = best_ask - best_bid
		if spread > self.spread:
			mid = (best_ask + best_bid) / 2 - pos / 10
			sell_for = int(np.round(mid + self.spread / 2))
			q = -self.single_position_limit
			q = max(q, -20 - pos - sell_q)
			q = min(q, 0)
			if q != 0:
				orders.append(Order(product, sell_for, q))
			
			buy_for = int(round(mid - self.spread / 2))
			q = self.single_position_limit
			q = min(q, 20 - pos - buy_q)
			q = max(q, 0)
			if q != 0:
				orders.append(Order(product, buy_for, q))
		
		return orders
	
	def order_amethysts(self, state: TradingState) -> list[Order]:
		orders = []
		product = "AMETHYSTS"
		
		order_depth = state.order_depths[product]
		pos = state.position.get(product, 0)
		limit_buy, limit_sell = 20 - pos, -20 - pos
		# buy cheap items
		
		q = calculate_buy_quantity(order_depth, self.target_price - 1)
		q = min(q, limit_buy)
		if q != 0:
			limit_buy -= q
			pos += q
			orders.append(Order(product, self.target_price - 1, q))
		#
		# sell expensive items
		q = calculate_sell_quantity(order_depth, self.target_price + 1)
		q = max(q, -20 - pos)
		if q != 0:
			limit_sell -= q
			pos += q
			orders.append(Order(product, self.target_price + 1, q))
		#
		
		# make 0 position
		if pos > 0:
			q = calculate_sell_quantity(order_depth, self.target_price)
			q = max(q, limit_sell)
			if q != 0:
				pos += q
				limit_sell -= q
				orders.append(Order(product, self.target_price, q))
		elif pos < 0:
			q = calculate_buy_quantity(order_depth, self.target_price)
			q = min(q, limit_buy)
			if q != 0:
				pos += q
				limit_buy -= q
				orders.append(Order(product, self.target_price, q))
		#
		
		# send MM orders
		buy_q = limit_buy
		sell_q = limit_sell
		if buy_q > 0:
			best_bid = max(order_depth.buy_orders.keys())
			buy_price = min(self.target_price - 2, best_bid + 1)
			orders.append(Order(product, buy_price + buy_q // 40, buy_q))
		if sell_q < 0:
			best_ask = min(order_depth.sell_orders.keys())
			sell_price = max(self.target_price + 2, best_ask - 1)
			orders.append(Order(product, sell_price + sell_q // 40 + 1, sell_q))
		
		# String value holding Trader state data required.
		# It will be delivered as TradingState.traderData on next execution.
		return orders
	
	def run(self, state: TradingState):
		self.runs += 1
		self.update_limit_hits(state)
		self.update_orchid_trades(state)
		# assert (self.prev_state.timestamp < state.timestamp)
		
		result = {
				"ORCHIDS": self.order_orchid(state),
				"STARFRUIT": self.order_starfruit(state),
				"AMETHYSTS": self.order_amethysts(state),
		}
		result.update(self.order_gift_basket(state))
		
		self.update_prevs("STARFRUIT", state)
		pos = state.position.get("ORCHIDS", 0)
		south_q = max(0, -pos)
		return result, south_q, ""
	
	def order_orchid(self, state: TradingState):
		product = "ORCHIDS"
		pos = state.position.get(product, 0)
		observation = state.observations.conversionObservations[product]
		
		print(f"OBSERVATION.askPrice: {observation.askPrice}")
		print(f"OBSERVATION.importTariff: {observation.importTariff}")
		print(f"OBSERVATION.transportFees: {observation.transportFees}")
		
		min_profitable_bid = round(
			observation.askPrice + observation.importTariff + observation.transportFees + self.min_bid_margin)
		
		q = calculate_sell_quantity(state.order_depths[product], min_profitable_bid)
		q = max(q, -self.limits[product] - pos)
		if q != 0:
			orders = [Order(product, min_profitable_bid, q)]
		else:
			orders = []
		
		# market making
		margin_values = list(range(0, 5))
		
		south_ask = observation.askPrice + observation.importTariff + observation.transportFees
		available_q = max(-self.limits[product] - pos - q, -self.limits[product])
		
		self.prev_south_ask = south_ask
		best_bid = max(state.order_depths[product].buy_orders.keys())
		self.prev_best_bid = best_bid
		
		if available_q < -len(margin_values):
			for margin in margin_values:
				small_q = -1
				ask_price = self.get_orchid_price(south_ask, best_bid, margin)
				orders.append(Order(product, ask_price, small_q))
		else:
			return orders
		
		available_q += len(margin_values)
		
		if len(self.orchid_spreads) < 0.1 * self.orchid_window:
			ask_price = int((south_ask + 1.5))
			orders.append(Order(product, ask_price, available_q))
			return orders
		
		probs = []
		for margin in margin_values:
			prob = sum([1.0 for x in self.orchid_spreads if x[1] == margin]) / len(
				self.orchid_spreads)
			probs.append((margin, prob))
		
		
		def profit_for_margin(margin):
			return self.get_orchid_price(south_ask, best_bid, margin) - south_ask
		
		expected_profits = [(x, y, profit_for_margin(x) * y) for x, y in probs]
		best_margin = max(expected_profits, key = lambda x: x[2])[0]
		print(f"Best margin: {best_margin}")
		
		ask_price = self.get_orchid_price(south_ask, best_bid, best_margin)
		if available_q < 0:
			orders.append(Order(product, ask_price, available_q))
		
		return orders
	
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
		          mid_price[
			          'STRAWBERRIES'] * 6 - 390
		res_sell = mid_price['GIFT_BASKET'] - mid_price['ROSES'] - mid_price['CHOCOLATE'] * 4 - \
		           mid_price[
			           'STRAWBERRIES'] * 6 - 390
		
		trade_at = self.basket_std * 0.5
		
		traded_product = "GIFT_BASKET"
		pb_pos = state.position.get(traded_product, 0)
		pb_neg = state.position.get(traded_product, 0)
		pos = state.position.get(traded_product, 0)
		lim = self.limits[traded_product]
		
		# print(state.position)
		if res_sell > trade_at:
			vol = pos + lim
			self.cont_buy_basket_unfill = 0  # no need to buy rn
			# assert (vol >= 0)
			if vol > 0:
				orders[traded_product].append(
						Order(traded_product, worst_buy[traded_product], -vol))
				pb_neg -= vol
		# uku_pos += vol
		elif res_buy < -trade_at:
			vol = lim - pos
			# assert (vol >= 0)
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
	
	def update_limit_hits(self, state: TradingState):
		for product in self.products:
			if product in state.position and state.position[product] == self.limits[product]:
				self.limit_hits_up[product] += 1
			elif product in state.position and state.position[product] == -self.limits[product]:
				self.limit_hits_down[product] += 1
		if self.verbose:
			print(f"Limit hits up: {self.limit_hits_up}")
			print(f"Limit hits down: {self.limit_hits_down}")
		return self.limit_hits_up, self.limit_hits_down
