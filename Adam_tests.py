from typing import List

from datamodel import OrderDepth, TradingState, Order


class Trader:

    def __init__(self):
        self.limit_hits_up = {}
        self.limit_hits_down = {}
        self.limits = {}
        self.runs = 0

        self.products = ["STARFRUIT", "AMETHYSTS"]
        for product in self.products:
            self.limit_hits_up[product] = 0
            self.limit_hits_down[product] = 0
            self.limits[product] = 20

    def run(self, state: TradingState):
        result = {}
        self.runs += 1
        for product in self.products:
            orders: List[Order] = []
            order_depth: OrderDepth = state.order_depths[product]
            if product in state.order_depths:
                pos = 0
                if product in state.position:
                    pos = state.position[product]

                if pos == self.limits[product]:
                    self.limit_hits_up[product] += 1
                elif pos == -self.limits[product]:
                    self.limit_hits_down[product] += 1

                if product == "AMETHYSTS":
                    amethyst_price = 10000#fair price
                    amethyst_buy = 9999#max price that we want to pay to buy
                    amethyst_sell = 10001#minimal price that we want to sell

                    if len(order_depth.sell_orders) != 0:
                        best_ask, best_ask_amount = list(order_depth.sell_orders.items())[0]  # sorted
                        if int(best_ask) < amethyst_price:#if best ask price is lower than fair we want to buy
                            if pos < 20:#check if we are full
                                buy_amount = 20 - pos#max that we can buy
                                orders.append(Order(product, amethyst_buy, buy_amount))#buy order
                        elif pos < 0:#if we are short on amethyst we want to buy at fair price
                            orders.append(Order(product, amethyst_price, -pos))#buy

                    if len(order_depth.buy_orders) != 0:
                        best_bid, best_bid_amount = list(order_depth.buy_orders.items())[0]
                        if int(best_bid) > amethyst_price:#if best bid price is higer than fair we want to sell
                            if pos > -20:#check if we are full
                                sell_amount = -20-pos
                                orders.append(Order(product, amethyst_sell, sell_amount))#sell
                        elif pos > 0:#if we have amethyst we want to sell at fair price
                            orders.append(Order(product, amethyst_price, -pos))#sell

                result[product] = orders
        #hits stock limit
        traderData = "SAMPLE"
        print(f"limits up: {self.limit_hits_up}, limits down: {self.limit_hits_down}\n")
        print(f"runs: {self.runs}\n")

        return result, 0, traderData
