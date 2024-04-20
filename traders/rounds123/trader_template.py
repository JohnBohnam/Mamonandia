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
        self.products = ["STARFRUIT", "AMETHYSTS", "ORCHIDS"]

        for product in self.products:
            self.limit_hits_up[product] = 0
            self.limit_hits_down[product] = 0
            self.limits[product] = 20

        self.limits["ORCHIDS"] = 100

        print("Trader initialized with params: ", self.__dict__)

    def run(self, state: TradingState):
        result = {"ORCHIDS": self.order_orchid(state),
                  "STARFRUIT": self.order_starfruit(state),
                  "AMEHTYSTS": self.order_amethysts(state),}
        self.run_routine(state)

        # conversions here (2nd tuple element)
        return result, 0, ""

    def run_routine(self, state: TradingState):
        self.update_limit_hits(state)
        self.runs += 1
        if self.verbose:
            print(f"Run {self.runs}")
            print(f"Position: {state.position}")
            print(f"Limit hits up: {self.limit_hits_up}")
            print(f"Limit hits down: {self.limit_hits_down}")

    def order_amethysts(self, state: TradingState):
        orders = []
        # ...
        return orders

    def order_starfruit(self, state: TradingState):
        orders = []
        # ...
        return orders

    def order_orchid(self, state: TradingState):
        orders = []
        # ...
        return orders

    def update_limit_hits(self, state: TradingState):
        for product in self.products:
            if product in state.position and state.position[product] == self.limits[product]:
                self.limit_hits_up[product] += 1
            elif product in state.position and state.position[product] == -self.limits[product]:
                self.limit_hits_down[product] += 1
        return self.limit_hits_up, self.limit_hits_down
