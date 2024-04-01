from typing import List

from datamodel import OrderDepth, TradingState, Order
import numpy as np


# bid (buy) - za ile kupią
# ask (sell) - za ile sprzedzadzą

# ujemna wartosc w order.quantity oznacza sprzedaz

class Trader:

    def __init__(self):
        self.limit_hits_up = {}
        self.limit_hits_down = {}
        self.limits = {}
        self.runs = 0
        self.prev_diff = None
        self.prev_price = None
        self.last_bid = None
        self.last_ask = None
        self.mode = "site"
        # self.mode = "local"

        self.magic_number = -0.45559303

        if self.mode == "local":
            self.products = ["BANANAS"]
        else:
            self.products = ["STARFRUIT"]
        for product in self.products:
            self.limit_hits_up[product] = 0
            self.limit_hits_down[product] = 0
            self.limits[product] = 20

        print(f"Trader initialized - mode: {self.mode} | products: {self.products}")

    def run(self, state: TradingState):
        if self.mode == "local":
            product = "BANANAS"
        else:
            product = "STARFRUIT"
        result = {}
        self.runs += 1
        print(f"limits up: {self.limit_hits_up}, limits down: {self.limit_hits_down}\n")
        print(f"runs: {self.runs}\n")
        position = state.position
        for product in self.products:
            if product in position and position[product] == self.limits[product]:
                self.limit_hits_up[product] += 1
            elif product in position and position[product] == -self.limits[product]:
                self.limit_hits_down[product] += 1

        if product not in state.order_depths:
            if self.mode == "local":
                return result
            else:
                return result, 0, ""

        od = state.order_depths[product]
        if len(od.buy_orders) != 0:
            self.last_bid = list(od.buy_orders.keys())[0]
        if len(od.sell_orders) != 0:
            self.last_ask = list(od.sell_orders.keys())[0]

        price = (self.last_bid + self.last_ask) / 2
        if self.prev_price is not None:
            diff = price - self.prev_price
            self.prev_diff = diff

            next_diff_pred = self.magic_number * diff
            next_price_pred = int(np.round(price + next_diff_pred))
            # buy if next price is higher than current price
            # sell if next price is lower than current price
            pos = position[product] if product in position else 0
            orders = [Order(product, next_price_pred + 1, -pos - 20), Order(product, next_price_pred - 1, 20 - pos)]
            print(f"buying {20 - pos} of {product} at {next_price_pred + 1}")
            print(f"selling {pos - 20} of {product} at {next_price_pred - 1}")
            result[product] = orders

        self.prev_price = price

        if self.mode == "local":
            return result
        else:
            return result, 0, ""
