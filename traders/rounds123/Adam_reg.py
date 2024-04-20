#from research.datamodel import TradingState, Order
from datamodel import TradingState, Order
import numpy as np


# bid (buy) - za ile kupią
# ask (sell) - za ile sprzedzadzą

# ujemna wartosc w order.quantity oznacza sprzedaz


class Trader:
    def calculate_buy_quantity(self, order_depth, target_price):
        asks = order_depth.sell_orders
        q = sum([-y for x, y in asks.items() if x <= target_price])
        return q

    def calculate_sell_quantity(self, order_depth, target_price):
        bids = order_depth.buy_orders
        q = sum([-y for x, y in bids.items() if x >= target_price])
        return q

    def set_params(self, **params):
        for key, value in params.items():
            setattr(self, key, value)

    def __init__(self, buy_margin=6, sell_margin=5, time_window=20, verbose=False):
        self.bullshit = 0
        self.limit_hits_up = {}
        self.limit_hits_down = {}
        self.limits = {}
        self.runs = 0
        self.prev_bids = []
        self.prev_asks = []

        # print(f"buy_margin: {buy_margin}, sell_margin: {sell_margin}, time_window: {time_window}")

        # the bigger the time window, the more conservative the trader
        self.time_window = time_window

        # the lesser the margin, the more aggressive the trader
        self.buy_margin = buy_margin
        self.sell_margin = sell_margin

        self.verbose = verbose

        # these are the stupid prams that make stupid profits
        # self.set_params(**{'buy_margin': 0.7850037515086065, 'sell_margin': 0.6388820974848624, 'time_window': 6.469020211030575})

        self.products = ["STARFRUIT", "AMETHYSTS"]

        for product in self.products:
            self.limit_hits_up[product] = 0
            self.limit_hits_down[product] = 0
            self.limits[product] = 20

    def update_prevs(self, product, state: TradingState):
        if product not in state.order_depths:
            return
        od = state.order_depths[product]

        bid_price = None
        if od.buy_orders:
            bid_price = min(od.buy_orders.keys())
        elif self.prev_bids:
            bid_price = self.prev_bids[-1]
            # print("no bids, using prev")

        if bid_price is not None:
            self.prev_bids.append(bid_price)

        ask_price = None
        if od.sell_orders:
            ask_price = max(od.sell_orders.keys())
        elif self.prev_asks:
            ask_price = self.prev_asks[0]
            # print("no asks, using prev")

        if ask_price is not None:
            self.prev_asks.append(ask_price)

        if len(self.prev_bids) > self.time_window:
            self.prev_bids.pop(0)
        if len(self.prev_asks) > self.time_window:
            self.prev_asks.pop(0)

    def order_starfruit(self, state: TradingState) -> list[Order]:
        #print("t")
        orders = []
        product = "STARFRUIT"
        if product not in state.order_depths:
            return orders
        if(len(self.prev_bids)>10):
           # print("t")
            max_w=[0.03324706,0.06035395,0.03408759,0.05620725,0.07770857,0.06575957,0.11965573,0.12771695,0.18420509,0.24105913]
            min_w=[0.02591859,0.03576816,0.03098156,0.07103187,0.06244842,0.08805917,0.10692855,0.14357695,0.19430629,0.24098119]
            last_min=np.array(self.prev_bids[-11:-1])
            last_max=np.array(self.prev_asks[-11:-1])
            exp_min=int(np.floor(np.dot(last_min, min_w)))
            exp_max=int(np.ceil(np.dot(last_max,max_w)))
            #print("min ",exp_min," max ",exp_max)
            pos = state.position[product] if product in state.position else 0
            qs = self.calculate_sell_quantity(state.order_depths["STARFRUIT"], exp_max-3)
            qs = max(qs, -20 - pos)

            qb = self.calculate_buy_quantity(state.order_depths["STARFRUIT"], exp_min+3)
            qb = min(qb, 20 - pos)
            orders.append(Order(product, exp_min+3, qb))
            orders.append(Order(product, exp_max-3, qs))

        return orders

    def order_amethysts(self, state: TradingState) -> list[Order]:
        product = "AMETHYSTS"
        amethyst_price = 10000  # fair price
        amethyst_buy = 9999  # max price that we want to pay to buy
        amethyst_sell = 10001  # minimal price that we want to sell

        orders = []
        if product not in state.order_depths:
            return orders

        pos = 0
        if product in state.position:
            pos = state.position[product]

        orders.append(Order(product, amethyst_buy, 20 - pos))
        orders.append(Order(product, amethyst_sell, -20 - pos))

        if orders:
            if self.verbose:
                print(f"orders for {product}: {orders}")
        return orders

    def run(self, state: TradingState):
        #print("t")
        self.runs += 1
        # print(f"limits up: {self.limit_hits_up}, limits down: {self.limit_hits_down}\n")
        # print(f"runs: {self.runs}\n")
        position = state.position
        for product in self.products:
            if product in position and position[product] == self.limits[product]:
                self.limit_hits_up[product] += 1
            elif product in position and position[product] == -self.limits[product]:
                self.limit_hits_down[product] += 1

        result = {"STARFRUIT": self.order_starfruit(state), "AMETHYSTS": []}#self.order_amethysts(state)}

        # print(result["AMETHYSTS"])

        self.update_prevs("STARFRUIT", state)

        return result, 0, ""

