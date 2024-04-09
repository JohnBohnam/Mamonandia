from typing import List, Dict

from datamodel import OrderDepth, TradingState, Order, Time
import numpy as np


def get_traded_volume(buy_orders: Dict[int, int], sell_orders: Dict[int, int], price):
    buy_volume = 0
    for bid_price, volume in buy_orders.items():
        if bid_price >= price:
            buy_volume += volume
    sell_volume = 0
    for ask_price, volume in sell_orders.items():
        if ask_price <= price:
            sell_volume += volume
    return min(buy_volume, sell_volume)


def get_fit_price(buy_orders: Dict[int, int], sell_orders: Dict[int, int]):
    if not buy_orders or not sell_orders:
        return None

    min_bid = min(buy_orders.keys())
    max_ask = max(sell_orders.keys())

    best_fit_price = None
    best_fit = 0
    for price in range(min_bid, max_ask):
        curr_fit = get_traded_volume(buy_orders, sell_orders, price)
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
        self.history_stairfruit: List[(Time, OrderDepth)] = []
        self.history_size = 20

        for product in self.products:
            self.limit_hits_up[product] = 0
            self.limit_hits_down[product] = 0
            self.limits[product] = 20

    def merge_dicts(self, list_of_dicts):
        merged_dict = {}
        for d in list_of_dicts:
            for key, value in d.items():
                if key in merged_dict:
                    merged_dict[key] += value
                else:
                    merged_dict[key] = value
        return merged_dict

    def get_historical_trades_for_stairfruit(self):
        result = [x[1] for x in self.history_stairfruit]
        return self.merge_dicts([x.buy_orders for x in result]), self.merge_dicts([x.sell_orders for x in result])

    def run(self, state: TradingState):
        self.runs += 1
        # print(f"limits up: {self.limit_hits_up}, limits down: {self.limit_hits_down}\n")
        # print(f"runs: {self.runs}\n")
        position = state.position
        self.history_stairfruit.append((state.timestamp, state.order_depths["STARFRUIT"]))
        self.history_stairfruit = self.history_stairfruit[-self.history_size:]

        for product in self.products:
            if product in position and position[product] == self.limits[product]:
                self.limit_hits_up[product] += 1
            elif product in position and position[product] == -self.limits[product]:
                self.limit_hits_down[product] += 1

        result = {"STARFRUIT": [], "AMETHYSTS": []}

        buy_orders, sell_orders = self.get_historical_trades_for_stairfruit()
        fit_price = get_fit_price(buy_orders, sell_orders)
        print(fit_price)

        return result, 0, ""
