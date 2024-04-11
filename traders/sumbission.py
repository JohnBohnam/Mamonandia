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

    def set_params(self, **params):
        for key, value in params.items():
            setattr(self, key, value)

    # good params so far: buy_margin=5, sell_margin=5, time_window=2, min_trend=0.000281, trend_sensitivity=1
    def __init__(self, buy_margin=4, sell_margin=4, time_window=2, verbose=False):
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


        # print(f"buy_margin: {buy_margin}, sell_margin: {sell_margin}, time_window: {time_window}")

        # the bigger the time window, the more conservative the trader
        self.time_window = time_window

        self.target_price = 10000


        # the lesser the margin, the more aggressive the trader
        self.buy_margin = buy_margin
        self.sell_margin = sell_margin

        self.verbose = verbose

        # these are the stupid prams that make stupid profits

        self.products = ["STARFRUIT", "AMETHYSTS"]

        for product in self.products:
            self.limit_hits_up[product] = 0
            self.limit_hits_down[product] = 0
            self.limits[product] = 20

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

        # od = state.order_depths[product]
        sell_margin = self.sell_margin
        buy_margin = self.buy_margin

        sell_q = 0
        buy_q = 0


        if self.prev_bids:
            sell_for = int(np.min(self.prev_bids) + sell_margin)
            # sell_q = -20-pos
            sell_q = calculate_sell_quantity(state.order_depths["STARFRUIT"], sell_for)
            sell_q = max(sell_q, -20 - pos)
            orders.append(Order(product, sell_for, sell_q))
            if self.verbose:
                print(f"pos: {pos}, selling {sell_q} of {product} for {sell_for}")

        if self.prev_asks:
            buy_for = int(np.max(self.prev_asks) - buy_margin)
            # buy_q = 20 - pos
            buy_q = calculate_buy_quantity(state.order_depths["STARFRUIT"], buy_for)
            buy_q = min(buy_q, 20 - pos)
            orders.append(Order(product, buy_for, buy_q))
            if self.verbose:
                print(f"pos: {pos}, buying {buy_q} of {product} for {buy_for}")
        # print(orders)

        # pos = state.position["STARFRUIT"] if "STARFRUIT" in state.position else 0
        best_bid = max(state.order_depths["STARFRUIT"].buy_orders.keys()) if state.order_depths[
            "STARFRUIT"].buy_orders else 0
        best_ask = min(state.order_depths["STARFRUIT"].sell_orders.keys()) if state.order_depths[
            "STARFRUIT"].sell_orders else 0
        spread = best_ask - best_bid
        if spread > self.spread:
            mid = (best_ask + best_bid) / 2 - pos / 10
            sell_for = int(np.round(mid + self.spread / 2))
            q = -self.single_position_limit
            q = max(q, -20 - pos - sell_q)
            q = min(q, 0)
            if q != 0:
                orders.append(Order("STARFRUIT", sell_for, q))

            buy_for = int(round(mid - self.spread / 2))
            q = self.single_position_limit
            q = min(q, 20 - pos - buy_q)
            q = max(q, 0)
            if q != 0:
                orders.append(Order("STARFRUIT", buy_for, q))

        return orders
    #
    # def order_amethysts(self, state: TradingState) -> list[Order]:
    #     orders = []
    #     product = "AMETHYSTS"
    #
    #     order_depth = state.order_depths[product]
    #     pos = state.position.get(product, 0)
    #     limit_buy, limit_sell = 20 - pos, -20 - pos
    #     # buy cheap items
    #
    #     q = calculate_buy_quantity(order_depth, self.target_price - 1)
    #     q = min(q, limit_buy)
    #     if q != 0:
    #         limit_buy -= q
    #         pos += q
    #         orders.append(Order(product, self.target_price - 1, q))
    #     #
    #     # sell expensive items
    #     q = calculate_sell_quantity(order_depth, self.target_price + 1)
    #     q = max(q, -20 - pos)
    #     if q != 0:
    #         limit_sell -= q
    #         pos += q
    #         orders.append(Order(product, self.target_price + 1, q))
    #     #
    #
    #     # make 0 position
    #     if pos > 0:
    #         q = calculate_sell_quantity(order_depth, self.target_price)
    #         q = max(q, limit_sell)
    #         if q != 0:
    #             pos += q
    #             limit_sell -= q
    #             orders.append(Order(product, self.target_price, q))
    #     elif pos < 0:
    #         q = calculate_buy_quantity(order_depth, self.target_price)
    #         q = min(q, limit_buy)
    #         if q != 0:
    #             pos += q
    #             limit_buy -= q
    #             orders.append(Order(product, self.target_price, q))
    #
    #     # send MM orders
    #     buy_q = limit_buy
    #     sell_q = limit_sell
    #     if buy_q > 0:
    #         orders.append(Order(product, self.target_price - 1 + buy_q // 40, buy_q))
    #     if sell_q < 0:
    #         orders.append(Order(product, self.target_price + 1 + sell_q // 40 + 1, sell_q))
    #
    #     return orders

    def order_amethysts(self, state: TradingState) -> list[Order]:
        orders = []
        product = "AMETHYSTS"

        order_depth = state.order_depths[product]
        pos = state.position.get(product, 0)
        limit_buy, limit_sell = 20 - pos, -20 - pos

        q = calculate_buy_quantity(order_depth, self.target_price - self.half_spread)
        q = min(q, limit_buy)
        if q != 0:
            limit_buy -= q
            pos += q
            orders.append(Order(product, self.target_price - self.half_spread, q))

        q = calculate_sell_quantity(order_depth, self.target_price + self.half_spread)
        q = max(q, -20 - pos)
        if q != 0:
            limit_sell -= q
            pos += q
            orders.append(Order(product, self.target_price + self.half_spread, q))

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

        # send MM orders
        buy_q = limit_buy
        sell_q = limit_sell
        if buy_q > 0:
            orders.append(Order(product, self.target_price - self.half_spread + buy_q // 40, buy_q))
        if sell_q < 0:
            orders.append(Order(product, self.target_price + self.half_spread + sell_q // 40 + 1, sell_q))
        return orders

    def run(self, state: TradingState):
        print(f"buy_margin: {self.buy_margin}, sell_margin: {self.sell_margin}, single_position_limit: {self.single_position_limit}")
        print(f"time_window: {self.time_window}")
        self.runs += 1
        # print(f"runs: {self.runs}\n")
        self.update_limit_hits(state)

        print(f"limit_hits_up: {self.limit_hits_up}, limit_hits_down: {self.limit_hits_down}")

        result = {"STARFRUIT": self.order_starfruit(state), "AMETHYSTS": self.order_amethysts(state)}
        # result = {"STARFRUIT": [], "AMETHYSTS": self.order_amethysts(state)}

        self.update_prevs("STARFRUIT", state)

        return result, 0, ""

    def update_limit_hits(self, state: TradingState):
        for product in self.products:
            if product in state.position and state.position[product] == self.limits[product]:
                self.limit_hits_up[product] += 1
            elif product in state.position and state.position[product] == -self.limits[product]:
                self.limit_hits_down[product] += 1
        return self.limit_hits_up, self.limit_hits_down
