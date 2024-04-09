from typing import List, Dict

from datamodel import OrderDepth, TradingState, Order
import numpy as np


def get_mid_price(od: OrderDepth):
    if not od.buy_orders or not od.sell_orders:
        return None
    # is this how it`s done?
    return (min(od.buy_orders.keys()) + max(od.sell_orders.keys())) // 2


def get_trader_volume(buy_orders: Dict[int, int], sell_orders: Dict[int, int], price):
    buy_volume = 0
    for bid_price, volume in buy_orders.items():
        if bid_price >= price:
            buy_volume += volume
    sell_volume = 0
    for ask_price, volume in sell_orders.items():
        if ask_price <= price:
            sell_volume += volume
    return min(buy_volume, sell_volume)


def fit_price(buy_orders: Dict[int, int], sell_orders: Dict[int, int]):
    if not buy_orders or not sell_orders:
        return None

    min_bid = min(buy_orders.keys())
    max_ask = max(sell_orders.keys())

    best_fit_price = None
    best_fit = 0
    for price in range(min_bid, max_ask):
        curr_fit = get_trader_volume(buy_orders, sell_orders, price)
        if curr_fit > best_fit:
            best_fit = curr_fit
            best_fit_price = price
    return best_fit_price


class Trader:

    def __init__(self, sell_margin=1, buy_margin=1, time_window=2, verbose=False):
        self.limit_hits_up = {}
        self.limit_hits_down = {}
        self.limits = {}
        self.runs = 0

        self.prev_mids = []
        self.buy_margin = sell_margin
        self.sell_margin = buy_margin
        self.time_window = time_window

        self.verbose = verbose

        self.products = ["STARFRUIT", "AMETHYSTS"]

        for product in self.products:
            self.limit_hits_up[product] = 0
            self.limit_hits_down[product] = 0
            self.limits[product] = 20

    def update_prevs(self, product, state: TradingState):
        if product not in state.order_depths:
            return
        od = state.order_depths[product]
        self.prev_mids.append(get_mid_price(od))

        if len(self.prev_mids) >= self.time_window:
            self.prev_mids.pop(0)

    def order_starfruit(self, state: TradingState) -> list[Order]:
        orders = []
        product = "STARFRUIT"
        if product not in state.order_depths:
            return orders

        pos = state.position[product] if product in state.position else 0

        if self.prev_mids:
            fair_price = int(np.median(self.prev_mids))
            sell_for = int(fair_price + self.sell_margin)
            orders.append(Order(product, sell_for, -20 - pos))
            if self.verbose:
                print(f"pos: {pos}, selling {-20 - pos} of {product} for {sell_for}")

            buy_for = int(fair_price - self.buy_margin)
            orders.append(Order(product, buy_for, 20 - pos))
            if self.verbose:
                print(f"pos: {pos}, buying {20 - pos} of {product} for {buy_for}")

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

        result = {"STARFRUIT": self.order_starfruit(state), "AMETHYSTS": []}

        self.update_prevs("STARFRUIT", state)

        return result, 0, ""
