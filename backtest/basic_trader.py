from datamodel import OrderDepth, UserId, TradingState, Order
from typing import List
import json
import string

from dontlooseshells_algo import Logger


class Trader:
	logger = Logger(local=True)
	traderData = ""
	def run(self, state: TradingState):
		if len(self.traderData) < 3:
			acceptable_price_dict = {"PEARLS": 10000, "BANANAS": 5000}
		else:
			acceptable_price_dict = json.loads(self.traderData)
		# Only method required. It takes all buy and sell orders for all symbols as an input,
		# and outputs a list of orders to be sent
		# print("traderData: " + self.traderData)
		# print("Observations: " + str(state.observations))
		result = {}
		for product in state.order_depths:
			order_depth: OrderDepth = state.order_depths[product]
			orders: List[Order] = []
			# if product =="AMETHYSTS":
			#     acceptable_price = 10000
			# if product =="STARFRUIT":
			#     acceptable_price = 5000
			# acceptable_price = 10  # Participant should calculate this value
			acceptable_price = acceptable_price_dict[product]
			# print(f"acceptable_price is {acceptable_price}")
			# print(f" position is {state.position}")
			
			if len(order_depth.sell_orders) != 0:
				best_ask, best_ask_amount = list(order_depth.sell_orders.items())[0]
				if int(best_ask) < acceptable_price:
					# print("BUY", str(-best_ask_amount) + "x", best_ask)
					orders.append(Order(product, best_ask, -best_ask_amount))
					acceptable_price_dict[product] = (best_ask + acceptable_price) / 2.0
			
			if len(order_depth.buy_orders) != 0:
				best_bid, best_bid_amount = list(order_depth.buy_orders.items())[0]
				if int(best_bid) > acceptable_price:
					# print("SELL", str(best_bid_amount) + "x", best_bid)
					orders.append(Order(product, best_bid, -best_bid_amount))
					acceptable_price_dict[product] = (best_bid + acceptable_price) / 2
			
			result[product] = orders
			self.logger.flush(state, result)
		
		return result