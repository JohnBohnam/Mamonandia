from typing import List, Dict
import numpy as np
from research.datamodel import OrderDepth, TradingState, Order, Time
# from datamodel import OrderDepth, TradingState, Order, Time


def get_traded_volume(buy_orders: Dict[int, int], sell_orders: Dict[int, int], price):
    buy_volume = 0
    for bid_price, volume in buy_orders.items():
        if bid_price >= price:
            buy_volume += volume
    sell_volume = 0
    for ask_price, volume in sell_orders.items():
        if ask_price <= price:
            sell_volume -= volume
    return buy_volume, sell_volume


def get_fit_price(buy_orders: Dict[int, int], sell_orders: Dict[int, int]):
    if not buy_orders or not sell_orders:
        return None
    
    potential_prices =sorted( list(buy_orders.keys()) + list(sell_orders.keys()))

    
    best_fit_price = None
    best_size = 0
    best_diff = 0
    count = 1
    for price in potential_prices:
        buy_size, sell_size = get_traded_volume(buy_orders, sell_orders, price)
        curr_size = min(buy_size, sell_size)
        curr_diff = abs(buy_size - sell_size)
        if curr_size > best_size or (curr_size == best_size and curr_diff < best_diff):
            best_size = curr_size
            best_diff = curr_diff
            best_fit_price = price
            count = 1
        elif curr_size == best_size and curr_diff == best_diff:
            best_fit_price = (best_fit_price * count + price) / (count + 1)
            count += 1
    if best_fit_price:
        best_fit_price = np.round(best_fit_price)
    return best_fit_price


class Trader:

    def __init__(self, sell_margin=1, buy_margin=1, time_window=20, verbose=False):
        self.limit_hits_up = {}
        self.limit_hits_down = {}
        self.limits = {}
        self.runs = 0

        self.prev_mids = []
        self.buy_margin = int(buy_margin)
        self.sell_margin = int(sell_margin)
        self.time_window = int(time_window)

        self.verbose = verbose

        self.products = ["STARFRUIT", "AMETHYSTS"]
        self.history_stairfruit: List[(Time, OrderDepth)] = []

        for product in self.products:
            self.limit_hits_up[product] = 0
            self.limit_hits_down[product] = 0
            self.limits[product] = 20
    
    def calculate_buy_quantity(self, order_depth, target_price):
        asks = order_depth.sell_orders
        q = sum([-y for x, y in asks.items() if x <= target_price])
        return q
    
    def calculate_sell_quantity(self, order_depth, target_price):
        bids = order_depth.buy_orders
        q = sum([-y for x, y in bids.items() if x >= target_price])
        return q
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
        print(f"timestamp: {state.timestamp}, position: {position}")
        self.history_stairfruit.append((state.timestamp, state.order_depths["STARFRUIT"]))
        self.history_stairfruit = self.history_stairfruit[-self.time_window:]

        for product in self.products:
            if product in position and position[product] == self.limits[product]:
                self.limit_hits_up[product] += 1
            elif product in position and position[product] == -self.limits[product]:
                self.limit_hits_down[product] += 1

        result = {"STARFRUIT": [], "AMETHYSTS": []}

        buy_orders, sell_orders = self.get_historical_trades_for_stairfruit()
        fit_price = get_fit_price(buy_orders, sell_orders)
        pos = state.position["STARFRUIT"] if "STARFRUIT" in state.position else 0
        if fit_price:
            sell_for = int(fit_price + self.sell_margin)
            q = self.calculate_sell_quantity(state.order_depths["STARFRUIT"], sell_for)
            q = max(q, -20 - pos)
            if q!=0:
                result["STARFRUIT"].append(Order("STARFRUIT", sell_for, q))
            if self.verbose:
                print("time", state.timestamp)
                print(f"pos: {pos}, selling {q} of STARFRUIT for {sell_for}")

            buy_for = int(fit_price - self.buy_margin)
            q = self.calculate_buy_quantity(state.order_depths["STARFRUIT"], buy_for)
            q = min(q, 20 - pos)
            if q!=0:
                result["STARFRUIT"].append(Order("STARFRUIT", buy_for, q))
            if self.verbose:
                print("time", state.timestamp)
                print(f"pos: {pos}, buying {q} of STARFRUIT for {buy_for}")
            if result["STARFRUIT"]:
                print(f"orders for STARFRUIT: {result['STARFRUIT']}")

        return result, 0, ""
