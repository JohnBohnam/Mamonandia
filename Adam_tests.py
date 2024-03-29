from datamodel import OrderDepth, UserId, TradingState, Order
from typing import List
import string


# - `STARFRUIT`: 20
# AMETHYSTS

class Trader:

    def __init__(self):
        self.products = ["STARFRUIT", "AMETHYSTS"]
        for product in self.products:
            print(f"{product} lowest ask price; {product} highest bid price;", end="")
        print(
            "obs bidPrice; obs askPrice; obs transportFees; obs exportTariff; obs importTariff; obs sunlight; obs humidity\n")
        # self.huj = 0

    def run(self, state: TradingState):
        result = {}
        for product in self.products:
            orders: List[Order] = []
            order_depth: OrderDepth = state.order_depths[product]
            if (product in state.order_depths):
                temp = list(order_depth.sell_orders.keys())
                temp.sort()
                temp_buy = list(order_depth.buy_orders.keys())
                temp_buy.sort()
                lowestAskPrice = temp[0]  # state.order_depths[product].keys().sort()[0]
                highestBidPrice = temp_buy[-1]
                mean=(lowestAskPrice+highestBidPrice)/2
                if product == "AMETHYSTS":
                    bid_price=9999
                    ask_price=10001
                #else:
                #    bid_price =4997
                #    ask_price = 5003
                #print(f"{lowestAskPrice}; {highestBidPrice};", end="")

               # mean_price = (lowestAskPrice + highestBidPrice) / 2
                    if len(order_depth.sell_orders) != 0:
                        best_ask, best_ask_amount = list(order_depth.sell_orders.items())[0]  # posortowane
                        if int(best_ask) < bid_price:
                            print("BUY", str(-best_ask_amount) + "x", best_ask)
                            orders.append(Order(product, ask_price, -best_ask_amount))

                    if len(order_depth.buy_orders) != 0:
                        best_bid, best_bid_amount = list(order_depth.buy_orders.items())[0]
                        if int(best_bid) > ask_price:
                            print("SELL", str(best_bid_amount) + "x", best_bid)
                            orders.append(Order(product, bid_price, -best_bid_amount))

                result[product] = orders

        # else:
        #    print("-1; -1;", end="")

        # String value holding Trader state data required.
        # It will be delivered as TradingState.traderData on next execution.
        traderData = "SAMPLE"

        return result, 0, traderData
