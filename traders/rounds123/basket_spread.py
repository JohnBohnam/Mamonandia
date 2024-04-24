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

	def __init__(self, buy_margin=4, sell_margin=4, time_window=2, verbose=True):
		self.limit_hits_up = {}
		self.limit_hits_down = {}
		self.limits = {}
		self.runs = 0
		self.prev_bids = []
		self.prev_asks = []
		self.prev_mids = []

		self.target_price = 10000
		self.half_spread = 2

		self.spread = 5
		self.single_position_limit = 5

		self.time_window = time_window

		self.target_price = 10000
		self.orchid_margin = 1.2

		self.min_bid_margin = 1

		self.buy_margin = buy_margin
		self.sell_margin = sell_margin

		self.basket_std_mult = 2.0

		self.verbose = verbose
		self.products = ['GIFT_BASKET', 'ROSES', 'CHOCOLATE', 'STRAWBERRIES']
		self.basket_coefs = {"GIFT_BASKET":1, 'ROSES': -1, 'CHOCOLATE': -4, 'STRAWBERRIES': -6}
		self.basket_history = {"mid_spread":[], "mid_point":[]}
		self.basket_history_len = 1000

		for product in self.products:
			self.limit_hits_up[product] = 0
			self.limit_hits_down[product] = 0
			self.limits[product] = 20

		self.limits["ORCHIDS"] = 100
		self.limits.update({"ROSES": 60, "CHOCOLATE": 250, "STRAWBERRIES": 350, "GIFT_BASKET": 60})

		print("Trader initialized with params: ", self.__dict__)



	

	def run(self, state: TradingState):
		self.runs += 1

		result = {}
		result.update(self.order_gift_basket(state))
		return result, 0, ""


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
		
		#update history
		spread_mid = mid_price['GIFT_BASKET']*self.basket_coefs['ROSES'] + mid_price['ROSES'] * self.basket_coefs['ROSES'] + mid_price['CHOCOLATE'] * self.basket_coefs['CHOCOLATE'] + mid_price['STRAWBERRIES'] * self.basket_coefs['STRAWBERRIES']
		self.basket_history["mid_spread"].append(spread_mid)
		self.basket_history["mid_spread"] = self.basket_history["mid_spread"][-self.basket_history_len:]
		def time_regression(x):
			time = np.linspace(0, len(x), len(x))
			coef = np.linalg.lstsq(time.reshape(-1, 1), x - np.mean(x), rcond = None)[0]
			return coef[0] * len(x)/2 + np.median(x)
		mid_point = time_regression(self.basket_history["mid_spread"])
		self.basket_history["mid_point"].append(mid_point)
		self.basket_history["mid_point"] = self.basket_history["mid_point"][-self.basket_history_len:]
		
		if len(self.basket_history["mid_point"]) < self.basket_history_len:
			return orders
		#
		# fee = np.std(np.array(self.basket_history["mid_spread"]) - np.array(self.basket_history["mid_point"])) * self.basket_std_mult
		fee = 100
		if spread_mid > mid_point + fee:
			target_q = -self.limits['GIFT_BASKET']
		elif spread_mid < mid_point - fee:
			target_q = self.limits['GIFT_BASKET']
		elif (spread_mid - mid_point)*state.position.get('GIFT_BASKET', 0) > 0:
			target_q = 0
		else:
			return orders
		print(f"position: {state.position}")
		current_q = state.position.get('GIFT_BASKET', 0)
		n_spreads = self.get_available_combination(state, self.basket_coefs, np.sign(target_q-current_q))
		n_spreads = min(n_spreads, abs(target_q - current_q))
		n_spreads = n_spreads * np.sign(target_q - current_q)
		print(f"n_spreads: {n_spreads}, target_q: {target_q}, current_q: {current_q}")
		if n_spreads > 0:
			for product in prods:
				q = (n_spreads + current_q) * self.basket_coefs[product] - state.position.get(product, 0)
				if q > 0:
					orders[product].append(Order(product, worst_sell[product], q))
				else:
					orders[product].append(Order(product, worst_buy[product], q))
		elif n_spreads < 0:
			for product in prods:
				q = (n_spreads + current_q) * self.basket_coefs[product] - state.position.get(product, 0)
				if q > 0:
					orders[product].append(Order(product, best_sell[product], q))
				else:
					orders[product].append(Order(product, best_buy[product], q))
		
		return orders
	def get_available_combination(self, state, weights:dict[str, int], side:int):
		if side ==-1:
			weights = {k: -v for k, v in weights.items()}
		result = {}
		for product, weight in weights.items():
			if weight < 0:
				available = abs(sum(state.order_depths[product].buy_orders.values()))
				q = min(available, abs(-self.limits[product] - state.position.get(product, 0)))
				result[product] = q//abs(weight)
			else:
				available = abs(sum(state.order_depths[product].sell_orders.values()))
				q = min(available, abs(self.limits[product] - state.position.get(product, 0)))
				result[product] = q//abs(weight)
		return min(result.values())
		
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
