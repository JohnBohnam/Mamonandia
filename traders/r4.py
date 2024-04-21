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

    def __init__(self, verbose=False):
        self.limit_hits_up = {}
        self.limit_hits_down = {}
        self.limits = {}
        self.runs = 0

        self.verbose = verbose
        self.products = ["STARFRUIT", "AMETHYSTS", "ORCHIDS", "COCONUT", "COCONUT_COUPON"]

        for product in self.products:
            self.limit_hits_up[product] = 0
            self.limit_hits_down[product] = 0
            self.limits[product] = 20

        self.limits["ORCHIDS"] = 100
        self.limits["COCONUT"] = 300
        self.limits["COCONUT_COUPON"] = 600

        print("Trader initialized with params: ", self.__dict__)

    def run(self, state: TradingState):
        result = {"COCONUT": self.order_coconut(state),
                  "COCONUT_COUPON": self.order_coupon(state)}
        self.run_routine(state)

        # conversions here (2nd tuple element)
        return result, 0, ""

    def eval_coconut(self, state: TradingState) -> (float, float):
        return 9999, 10001

    def eval_coupon(self, state: TradingState) -> (float, float):
        return 600, 610

    def order_coconut(self, state: TradingState):
        orders = []
        product = "COCONUT"

        if product not in state.order_depths:
            return orders

        pos = state.position.get(product, 0)

        best_bid = 0
        best_ask = 0
        if state.order_depths[product].sell_orders:
            best_ask = min(state.order_depths[product].sell_orders.keys())
        if state.order_depths[product].buy_orders:
            best_bid = max(state.order_depths[product].buy_orders.keys())

        coc_low, coc_high = self.eval_coconut(state)

        if best_ask <= coc_low:
            q = calculate_buy_quantity(state.order_depths[product], coc_low)
            q = min(q, self.limits[product] - pos)
            if q > 0:
                orders.append(Order(product, coc_low, q))
        if best_bid >= coc_high:
            q = calculate_sell_quantity(state.order_depths[product], coc_high)
            q = max(q, -self.limits[product] - pos)
            if q < 0:
                orders.append(Order(product, coc_high, q))

        return orders

    def order_coupon(self, state: TradingState):
        orders = []
        product = "COCONUT_COUPON"

        if product not in state.order_depths:
            return orders

        pos = state.position.get(product, 0)

        best_bid = 0
        best_ask = 0
        if state.order_depths[product].sell_orders:
            best_ask = min(state.order_depths[product].sell_orders.keys())
        if state.order_depths[product].buy_orders:
            best_bid = max(state.order_depths[product].buy_orders.keys())

        coup_low, coup_high = self.eval_coupon(state)

        if best_ask <= coup_low:
            q = calculate_buy_quantity(state.order_depths[product], coup_low)
            q = min(q, self.limits[product] - pos)
            if q > 0:
                orders.append(Order(product, coup_low, q))
        if best_bid >= coup_high:
            q = calculate_sell_quantity(state.order_depths[product], coup_high)
            q = max(q, -self.limits[product] - pos)
            if q < 0:
                orders.append(Order(product, coup_high, q))

        return orders


    def run_routine(self, state: TradingState):
        self.update_limit_hits(state)
        self.runs += 1
        if self.verbose:
            print(f"Run {self.runs}")
            print(f"Position: {state.position}")
            print(f"Limit hits up: {self.limit_hits_up}")
            print(f"Limit hits down: {self.limit_hits_down}")

    def update_limit_hits(self, state: TradingState):
        for product in self.products:
            if product in state.position and state.position[product] == self.limits[product]:
                self.limit_hits_up[product] += 1
            elif product in state.position and state.position[product] == -self.limits[product]:
                self.limit_hits_down[product] += 1
        return self.limit_hits_up, self.limit_hits_down
