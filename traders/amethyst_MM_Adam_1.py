# from research.datamodel import TradingState, Order
from datamodel import TradingState, Order


# - `STARFRUIT`: 20
# AMETHYSTS

class Trader:

    def __init__(self):
        self.target_price = 10000
        self.half_spread = 1

    def calculate_buy_quantity(self, order_depth, target_price):
        asks = order_depth.sell_orders
        q = sum([-y for x, y in asks.items() if x <= target_price])
        return q

    def calculate_sell_quantity(self, order_depth, target_price):
        bids = order_depth.buy_orders
        q = sum([-y for x, y in bids.items() if x >= target_price])
        return q

    def order_amethysts(self, state: TradingState):
        orders = []
        product = "AMETHYSTS"

        order_depth = state.order_depths[product]
        pos = state.position.get(product, 0)
        limit_buy, limit_sell = 20 - pos, -20 - pos

        q = self.calculate_buy_quantity(order_depth, self.target_price - self.half_spread)
        q = min(q, limit_buy)
        if q != 0:
            limit_buy -= q
            pos += q
            orders.append(Order(product, self.target_price - self.half_spread, q))

        q = self.calculate_sell_quantity(order_depth, self.target_price + self.half_spread)
        q = max(q, -20 - pos)
        if q != 0:
            limit_sell -= q
            pos += q
            orders.append(Order(product, self.target_price + self.half_spread, q))

        if pos > 0:
            q = self.calculate_sell_quantity(order_depth, self.target_price)
            q = max(q, limit_sell)
            if q != 0:
                pos += q
                limit_sell -= q
                orders.append(Order(product, self.target_price, q))
        elif pos < 0:
            q = self.calculate_buy_quantity(order_depth, self.target_price)
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
            orders.append(Order(product, self.target_price - self.half_spread + buy_q // 40, buy_q))
        if sell_q < 0:
            orders.append(Order(product, self.target_price + self.half_spread + sell_q // 40 + 1, sell_q))
        return orders

    def run(self, state: TradingState):
        result = {"STARFRUIT": [], "AMETHYSTS": self.order_amethysts(state)}

        return result, 0, ""
