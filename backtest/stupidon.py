from typing import List

from datamodel import OrderDepth, TradingState, Order
import numpy as np


# bid (buy) - za ile kupią
# ask (sell) - za ile sprzedzadzą

# ujemna wartosc w order.quantity oznacza sprzedaz


class Trader:

    def __init__(self):
        self.bullshit = 0
        self.limit_hits_up = {}
        self.limit_hits_down = {}
        self.limits = {}
        self.runs = 0
        self.prev_bids = []
        self.prev_asks = []

        # the bigger the time window, the more conservative the trader
        self.time_window = 2

        # the lesser the margin, the more aggressive the trader
        self.buy_margin = 6
        self.sell_margin = 5

        self.mode = "site"
        # self.mode = "local"

        if self.mode == "local":
            self.products = ["BANANAS"]
        else:
            self.products = ["STARFRUIT"]

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
            print("no bids, using prev")

        if bid_price is not None:
            self.prev_bids.append(bid_price)

        ask_price = None
        if od.sell_orders:
            ask_price = max(od.sell_orders.keys())
        elif self.prev_asks:
            ask_price = self.prev_asks[0]
            print("no asks, using prev")

        if ask_price is not None:
            self.prev_asks.append(ask_price)

        if len(self.prev_bids) > self.time_window:
            self.prev_bids.pop(0)
        if len(self.prev_asks) > self.time_window:
            self.prev_asks.pop(0)

    def run(self, state: TradingState):
        if self.mode == "local":
            product = "BANANAS"
        else:
            product = "STARFRUIT"
        self.runs += 1
        print(f"limits up: {self.limit_hits_up}, limits down: {self.limit_hits_down}\n")
        print(f"runs: {self.runs}\n")
        position = state.position
        for product in self.products:
            if product in position and position[product] == self.limits[product]:
                self.limit_hits_up[product] += 1
            elif product in position and position[product] == -self.limits[product]:
                self.limit_hits_down[product] += 1

        result = {}
        if product not in state.order_depths:
            if self.mode == "local":
                return result
            else:
                return result, 0, ""

        orders = []
        pos = position[product] if product in position else 0

        print(f"prev bids: {self.prev_bids}")
        print(f"prev asks: {self.prev_asks}")

        if self.prev_bids:
            sell_for = int(np.min(self.prev_bids) + self.sell_margin)
            orders.append(Order(product, sell_for, -20-pos))
            print(f"selling {-20-pos} of {product} for {sell_for}")

        if self.prev_asks:
            buy_for = int(np.max(self.prev_asks) - self.buy_margin)
            orders.append(Order(product, buy_for, 20-pos))
            print(f"buying {20-pos} of {product} for {buy_for}")

        result[product] = orders

        self.update_prevs(product, state)

        if self.mode == "local":
            return result
        else:
            return result, 0, ""

