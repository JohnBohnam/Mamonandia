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
        self.selected_keys = ["askPrice", "importTariff", "transportFees"]

    def run(self, state: TradingState):
        best_bid = max(state.order_depths["ORCHIDS"].buy_orders.keys())
        best_ask = min(state.order_depths["ORCHIDS"].sell_orders.keys())
        #
        self.info_dict = {"time": state.timestamp, "best_bid": best_bid, "best_ask": best_ask,
                     "position": state.position.get("ORCHIDS", 0), }
        observation = state.observations.conversionObservations["ORCHIDS"].__dict__
        observation = {k: observation[k] for k in self.selected_keys}
        self.info_dict.update(observation)
        
        result = {"ORCHIDS": self.order_orchid(state),
                  "STARFRUIT": self.order_starfruit(state),
                  "AMEHTYSTS": self.order_amethysts(state), }
        # self.run_routine(state)
        print(f"{self.info_dict}")
        # conversions here (2nd tuple element)
        pos = state.position.get("ORCHIDS", 0)
        south_q = max(0, -pos)
        return result, south_q, ""

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
        product = "ORCHIDS"
        pos = state.position.get(product, 0)
        observation = state.observations.conversionObservations[product]

        min_profitable_bid = int(observation.askPrice + observation.importTariff + observation.transportFees) + 1
        #sell orders
        q = calculate_sell_quantity(state.order_depths[product], min_profitable_bid)
        q = max(q, -self.limits[product] - pos)
        if q!=0:
            self.info_dict["market take position"] = q
            orders = [Order(product, min_profitable_bid, q)]
        else:
            orders = []

        # market making
        south_ask =observation.askPrice + observation.importTariff + observation.transportFees
        available_q = max(-self.limits[product] - pos - q, -self.limits[product]//2)
        ask_price = int(south_ask + 3)
        q = available_q
        if q < 0:
            self.info_dict["market make position"] = q
            # self.info_dict["MM_spread"] = ask_price - south_ask
            orders.append(Order(product, ask_price, q))
        return orders

    def update_limit_hits(self, state: TradingState):
        for product in self.products:
            if product in state.position and state.position[product] == self.limits[product]:
                self.limit_hits_up[product] += 1
            elif product in state.position and state.position[product] == -self.limits[product]:
                self.limit_hits_down[product] += 1
        return self.limit_hits_up, self.limit_hits_down
