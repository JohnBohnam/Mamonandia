from research.datamodel import OrderDepth, TradingState, Order
import numpy as np


def get_mid_price(od: OrderDepth):
    if not od.buy_orders or not od.sell_orders:
        return None
    # is this how it`s done?
    return (min(od.buy_orders.keys()) + max(od.sell_orders.keys())) // 2


class Trader:

    def __init__(self, sell_margin=1, buy_margin=1, time_window=6, verbose=False, position_margin = 3.0, trend_multiplier=10, history_length=100):
        self.limit_hits_up = {}
        self.limit_hits_down = {}
        self.limits = {}
        self.runs = 0

        self.prev_mids = []
        self.buy_margin = sell_margin
        self.sell_margin = buy_margin
        self.time_window = time_window
        self.position_margin = position_margin
        self.trend_multiplier = trend_multiplier
        self.history_length = history_length
        self.best_bids = []
        self.best_asks = []
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
            
        best_bid = max(state.order_depths[product].buy_orders.keys())
        best_ask = min(state.order_depths[product].sell_orders.keys())
        self.best_bids.append(best_bid)
        self.best_asks.append(best_ask)
        self.best_bids = self.best_bids[-self.history_length:]
        self.best_asks = self.best_asks[-self.history_length:]
        
    def get_trend(self):
        if len(self.best_bids) + len(self.best_asks) < 2*self.history_length:
            return 0
        #upward
        start = np.median(self.best_asks[:5])
        end = np.median(self.best_asks[-5:])
        trend = 0
        if start < end and np.argmax(self.best_asks) >0.8*self.history_length:
            trend = (end-start)/self.history_length
        #
        
        #downward
        start = np.median(self.best_bids[:5])
        end = np.max(self.best_bids[-5:])
        if start > end and np.argmin(self.best_bids) >0.8*self.history_length:
            trend = (end-start)/self.history_length
        return trend

    def order_starfruit(self, state: TradingState) -> list[Order]:
        orders = []
        product = "STARFRUIT"
        if product not in state.order_depths:
            return orders

        pos = state.position.get(product, 0)


        if self.prev_mids:
            trend_margin = self.get_trend() * self.trend_multiplier
            total_buy_margin = self.buy_margin + pos * self.position_margin/self.limits[product] - trend_margin
            total_sell_margin = self.sell_margin +(-pos) * self.position_margin/self.limits[product] + trend_margin
            fair_price = int(round(np.median(self.prev_mids)))
            sell_for = int(round(fair_price  + total_sell_margin))
            buy_orders = state.order_depths[product].buy_orders
            q = sum([quantity for price, quantity in buy_orders.items() if price > fair_price])
            q = max(-q, -20-pos)
            orders.append(Order(product, sell_for, q))
            if self.verbose and q!=0:
                print(f"time {state.timestamp} pos: {pos}, selling {q} of {product} for {sell_for} buy orders: {buy_orders}")

            buy_for = int(round(fair_price - total_buy_margin))
            sell_orders = state.order_depths[product].sell_orders
            q = sum([-quantity for price, quantity in sell_orders.items() if price < fair_price])
            q = min(q, 20-pos)
            orders.append(Order(product, buy_for, q))
            if self.verbose and q!=0:
                print(f"time {state.timestamp}, pos: {pos}, buying {q} of {product} for {buy_for}")

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
