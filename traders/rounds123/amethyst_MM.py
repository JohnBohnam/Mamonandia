# from research.datamodel import TradingState, Order
from datamodel import TradingState, Order

# - `STARFRUIT`: 20
# AMETHYSTS

class Trader:
	
	def calculate_buy_quantity(self, order_depth, target_price):
		asks = order_depth.sell_orders
		q = sum([-y for x, y in asks.items() if x <= target_price])
		return q
	
	def calculate_sell_quantity(self, order_depth, target_price):
		bids = order_depth.buy_orders
		q = sum([-y for x, y in bids.items() if x >= target_price])
		return q
	

	target_price = 10000
	def run(self, state: TradingState):
		result = {"STARFRUIT": [], "AMETHYSTS": []}
		orders = []
		product = "AMETHYSTS"
		
		
		order_depth = state.order_depths[product]
		pos = state.position.get(product, 0)
		limit_buy, limit_sell = 20 - pos, -20-pos
		# buy cheap items
		
		q = self.calculate_buy_quantity(order_depth, self.target_price-1)
		q = min(q, limit_buy)
		if q!=0:
			limit_buy-=q
			pos+=q
			orders.append(Order(product, self.target_price-1, q))
		#
		# sell expensive items
		q = self.calculate_sell_quantity(order_depth, self.target_price+1)
		q = max(q, -20-pos)
		if q!=0:
			limit_sell-=q
			pos+=q
			orders.append(Order(product, self.target_price+1, q))
		#
		
		#make 0 position
		if pos>0:
			q = self.calculate_sell_quantity(order_depth, self.target_price)
			q = max(q, limit_sell)
			if q!=0:
				pos+=q
				limit_sell-=q
				orders.append(Order(product, self.target_price, q))
		elif pos<0:
			q = self.calculate_buy_quantity(order_depth, self.target_price)
			q = min(q, limit_buy)
			if q!=0:
				pos+=q
				limit_buy-=q
				orders.append(Order(product, self.target_price, q))
		#
		
		# send MM orders
		buy_q = limit_buy
		sell_q = limit_sell
		if buy_q>0:
			best_bid = max(order_depth.buy_orders.keys())
			buy_price = min(self.target_price-2, best_bid+1)
			orders.append(Order(product,buy_price + buy_q//40, buy_q))
		if sell_q<0:
			best_ask = min(order_depth.sell_orders.keys())
			sell_price = max(self.target_price+2, best_ask-1)
			orders.append(Order(product, sell_price + sell_q//40+1, sell_q))
	
	# String value holding Trader state data required.
	# It will be delivered as TradingState.traderData on next execution.
		traderData = "SAMPLE"
		result[product] = orders
		print(f"pos: {pos}, orders for {product}: {orders}")
		return (result, 0, traderData)
