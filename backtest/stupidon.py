from typing import List

from datamodel import OrderDepth, TradingState, Order
import numpy as np


# bid (buy) - za ile kupią
# ask (sell) - za ile sprzedzadzą

# ujemna wartosc w order.quantity oznacza sprzedaz


class Trader:

    def set_params(self, **params):
        for key, value in params.items():
            setattr(self, key, value)

    def __init__(self, buy_margin=6, sell_margin=5, time_window=2, verbose=False):
        self.bullshit = 0
        self.limit_hits_up = {}
        self.limit_hits_down = {}
        self.limits = {}
        self.runs = 0
        self.prev_bids = []
        self.prev_asks = []

        # print(f"buy_margin: {buy_margin}, sell_margin: {sell_margin}, time_window: {time_window}")

        # the bigger the time window, the more conservative the trader
        self.time_window = time_window

        # the lesser the margin, the more aggressive the trader
        self.buy_margin = buy_margin
        self.sell_margin = sell_margin

        self.verbose = verbose

        # these are the stupid prams that make stupid profits
        # self.set_params(**{'buy_margin': 0.7850037515086065, 'sell_margin': 0.6388820974848624, 'time_window': 6.469020211030575})

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

        if self.prev_bids:
            sell_for = int(np.min(self.prev_bids) + self.sell_margin)
            orders.append(Order(product, sell_for, -20 - pos))
            if self.verbose:
                print(f"pos: {pos}, selling {-20 - pos} of {product} for {sell_for}")

        if self.prev_asks:
            buy_for = int(np.max(self.prev_asks) - self.buy_margin)
            orders.append(Order(product, buy_for, 20 - pos))
            if self.verbose:
                print(f"pos: {pos}, buying {20 - pos} of {product} for {buy_for}")

        return orders

    def order_amethysts(self, state: TradingState) -> list[Order]:
        product = "AMETHYSTS"
        amethyst_price = 10000  # fair price
        amethyst_buy = 9999  # max price that we want to pay to buy
        amethyst_sell = 10001  # minimal price that we want to sell

        orders = []
        if product not in state.order_depths:
            return orders

        pos = 0
        if product in state.position:
            pos = state.position[product]

        orders.append(Order(product, amethyst_buy, 20 - pos))
        orders.append(Order(product, amethyst_sell, -20 - pos))

        if orders:
            if self.verbose:
                print(f"orders for {product}: {orders}")
        return orders

    def run(self, state: TradingState):

        self.runs += 1
        # print(f"limits up: {self.limit_hits_up}, limits down: {self.limit_hits_down}\n")
        # print(f"runs: {self.runs}\n")
        position = state.position
        for product in self.products:
            if product in position and position[product] == self.limits[product]:
                self.limit_hits_up[product] += 1
            elif product in position and position[product] == -self.limits[product]:
                self.limit_hits_down[product] += 1

        result = {"STARFRUIT": self.order_starfruit(state), "AMETHYSTS": self.order_amethysts(state)}

        # print(result["AMETHYSTS"])

        self.update_prevs("STARFRUIT", state)

        return result, 0, ""

