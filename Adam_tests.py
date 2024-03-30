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
                # temp = list(order_depth.sell_orders.keys())
                # temp.sort()
                # temp_buy = list(order_depth.buy_orders.keys())
                # temp_buy.sort()
                # lowestAskPrice = temp[0]  # state.order_depths[product].keys().sort()[0]
                # highestBidPrice = temp_buy[-1]

                if product == "AMETHYSTS":
                    amethyst_price = 10000
                    amethyst_buy = 10001
                    amethyst_sell = 9999
                    pos = 0
                    if product in state.position:
                        pos = state.position[product]

                    if len(order_depth.sell_orders) != 0:
                        best_ask, best_ask_amount = list(order_depth.sell_orders.items())[0]  # posortowane
                        if int(best_ask) < amethyst_price:
                            # print("BUY", str(-best_ask_amount) + "x", best_ask)
                            if pos > -20:
                                buy_amount = 20 - pos
                                orders.append(Order(product, amethyst_buy, buy_amount))
                        elif pos < 0:
                            orders.append(Order(product, amethyst_price, -pos))

                    if len(order_depth.buy_orders) != 0:
                        best_bid, best_bid_amount = list(order_depth.buy_orders.items())[0]
                        if int(best_bid) > amethyst_price:
                            # print("SELL", str(best_bid_amount) + "x", best_bid)
                            if pos < 20:
                                sell_amount = 20 + pos
                                orders.append(Order(product, amethyst_sell, -sell_amount))
                    elif pos > 0:
                        orders.append(Order(product, amethyst_price, -pos))

                result[product] = orders

        traderData = "SAMPLE"
        print(f"limits up: {self.limit_hits_up}, limits down: {self.limit_hits_down}\n")
        print(f"runs: {self.runs}\n")

        return result, 0, traderData
