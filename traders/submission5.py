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

    def __init__(self, buy_margin=4, sell_margin=4, time_window=2, verbose=True):
        self.limit_hits_up = {}
        self.limit_hits_down = {}
        self.limits = {}
        self.runs = 0
        self.prev_bids = []
        self.prev_asks = []
        self.prev_mids = []

        self.coc_margin = 4
        self.coup_margin = 12

        self.target_price = 10000
        self.half_spread = 2

        self.time_window = time_window
        self.buy_margin = buy_margin
        self.sell_margin = sell_margin

        self.spread = 5
        self.single_position_limit = 5

        self.prev_south_ask = None
        self.prev_best_bid = None
        self.orchid_margin = 1.2
        self.orchid_window = 100
        self.orchid_spreads = []
        self.min_bid_margin = 1
        self.basket_std = 76

        self.verbose = verbose
        self.products = ["STARFRUIT", "AMETHYSTS", "ORCHIDS", "COCONUT", "COCONUT_COUPON"]
        self.coconut_window = 100

        for product in self.products:
            self.limit_hits_up[product] = 0
            self.limit_hits_down[product] = 0
            self.limits[product] = 20

        self.limits["ORCHIDS"] = 100
        self.limits["COCONUT"] = 300
        self.limits["COCONUT_COUPON"] = 600
        self.coconut_window = 1000
        self.coconut_spread_history = []
        self.coconut_prev_mids = {"COCONUT": None, "COCONUT_COUPON": None}
        self.coconut_multipliers = {"COCONUT": -1, "COCONUT_COUPON": 2}
        self.coconut_spread_limit = 30
        self.target_n_spreads = 0

        print("Trader initialized with params: ", self.__dict__)

    def run(self, state: TradingState):
        south_q = 0
        self.runs += 1
        result = {}
        try:
            # fuck python
            self.update_limit_hits(state)
            self.update_orchid_trades(state)
            # assert (self.prev_state.timestamp < state.timestamp)

            result = {
                "ORCHIDS": self.order_orchid(state),
                "STARFRUIT": self.order_starfruit(state),
                "AMETHYSTS": self.order_amethysts(state),
                # "COCONUT": self.order_coconut(state),
                # "COCONUT_COUPON": self.order_coupon(state),
            }

            result.update(self.order_spread(state))

            self.update_prevs("STARFRUIT", state)
            pos = state.position.get("ORCHIDS", 0)
            south_q = max(0, -pos)
        except Exception as e:
            print(f"Error in run: {e}, run = {self.runs}")

        return result, south_q, ""

    def get_orchid_price(self, south_ask, best_bid, margin):
        return int(south_ask + 1.5) + margin

    def update_orchid_trades(self, state: TradingState):
        if "ORCHIDS" not in state.own_trades:
            return 0
        curr_trades = []
        for trade in state.own_trades["ORCHIDS"]:
            if trade.timestamp == state.timestamp - 100:
                curr_trades.append(trade)
        sells = [trade.price for trade in curr_trades if trade.seller == "SUBMISSION"]

        if sells:
            max_sell = max(sells)
            curr_spread = max_sell - self.get_orchid_price(self.prev_south_ask,
                                                           self.prev_best_bid, 0)
        else:
            return 0

        self.orchid_spreads.append((state.timestamp, curr_spread))

        self.orchid_spreads = [(x, y) for x, y in self.orchid_spreads if
                               state.timestamp - x < self.orchid_window * 100]
        return curr_spread

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
        orders = []
        product = "STARFRUIT"
        if product not in state.order_depths:
            return orders

        pos = state.position[product] if product in state.position else 0

        sell_margin = self.sell_margin
        buy_margin = self.buy_margin

        sell_q = 0
        buy_q = 0

        lim = self.limits[product]

        ods = state.order_depths[product]

        if self.prev_bids:
            sell_for = int(np.min(self.prev_bids) + sell_margin)
            sell_q = calculate_sell_quantity(ods, sell_for)
            sell_q = max(sell_q, -lim - pos)
            orders.append(Order(product, sell_for, sell_q))
            if self.verbose:
                print(f"pos: {pos}, selling {sell_q} of {product} for {sell_for}")

        if self.prev_asks:
            buy_for = int(np.max(self.prev_asks) - buy_margin)
            buy_q = calculate_buy_quantity(ods, buy_for)
            buy_q = min(buy_q, lim - pos)
            orders.append(Order(product, buy_for, buy_q))
            if self.verbose:
                print(f"pos: {pos}, buying {buy_q} of {product} for {buy_for}")

        best_bid = max(ods.buy_orders.keys()) if ods.buy_orders else 0
        best_ask = min(ods.sell_orders.keys()) if ods.sell_orders else 0
        spread = best_ask - best_bid
        if spread > self.spread:
            mid = (best_ask + best_bid) / 2 - pos / 10
            sell_for = int(np.round(mid + self.spread / 2))
            q = -self.single_position_limit
            q = max(q, -20 - pos - sell_q)
            q = min(q, 0)
            if q != 0:
                orders.append(Order(product, sell_for, q))

            buy_for = int(round(mid - self.spread / 2))
            q = self.single_position_limit
            q = min(q, 20 - pos - buy_q)
            q = max(q, 0)
            if q != 0:
                orders.append(Order(product, buy_for, q))

        return orders

    def order_amethysts(self, state: TradingState) -> list[Order]:
        orders = []
        product = "AMETHYSTS"

        order_depth = state.order_depths[product]
        pos = state.position.get(product, 0)
        limit_buy, limit_sell = 20 - pos, -20 - pos
        # buy cheap items

        q = calculate_buy_quantity(order_depth, self.target_price - 1)
        q = min(q, limit_buy)
        if q != 0:
            limit_buy -= q
            pos += q
            orders.append(Order(product, self.target_price - 1, q))
        #
        # sell expensive items
        q = calculate_sell_quantity(order_depth, self.target_price + 1)
        q = max(q, -20 - pos)
        if q != 0:
            limit_sell -= q
            pos += q
            orders.append(Order(product, self.target_price + 1, q))
        #

        # make 0 position
        if pos > 0:
            q = calculate_sell_quantity(order_depth, self.target_price)
            q = max(q, limit_sell)
            if q != 0:
                pos += q
                limit_sell -= q
                orders.append(Order(product, self.target_price, q))
        elif pos < 0:
            q = calculate_buy_quantity(order_depth, self.target_price)
            q = min(q, limit_buy)
            if q != 0:
                pos += q
                limit_buy -= q
                orders.append(Order(product, self.target_price, q))
        #

        # send MM orders
        buy_q = limit_buy
        sell_q = limit_sell
        if buy_q > 0:
            best_bid = max(order_depth.buy_orders.keys())
            buy_price = min(self.target_price - 2, best_bid + 1)
            orders.append(Order(product, buy_price + buy_q // 40, buy_q))
        if sell_q < 0:
            best_ask = min(order_depth.sell_orders.keys())
            sell_price = max(self.target_price + 2, best_ask - 1)
            orders.append(Order(product, sell_price + sell_q // 40 + 1, sell_q))

        # String value holding Trader state data required.
        # It will be delivered as TradingState.traderData on next execution.
        return orders

    def eval_coconut(self, state: TradingState) -> (float, float):
        mids = {}
        for product in ["COCONUT", "COCONUT_COUPON"]:
            best_bid = max(state.order_depths[product].buy_orders.keys())
            best_ask = min(state.order_depths[product].sell_orders.keys())
            mids[product] = (best_bid + best_ask) / 2
        x = mids["COCONUT_COUPON"] - 600
        if x <= 0:
            regression_coeffs = [(-26.80799835, 1.54459215), (-78.17969157, 1.59804532)]
            prices = [x * a[1] + a[0] for a in regression_coeffs]
            return int(round(min(prices)+10000)), int(round(max(prices)+10000))
        if x > 0:
            regression_coeffs = [(-61.22517152, 1.75887911), (-15.22083538, 1.20576268), (-59.73260114, 2.50990171)]
            prices = [x * a[1] + a[0] for a in regression_coeffs]
            return int(round(min(prices)+10000)), int(round(max(prices)+10000))

    def eval_coupon(self, state: TradingState) -> (float, float):
        mids = {}
        for product in ["COCONUT", "COCONUT_COUPON"]:
            best_bid = max(state.order_depths[product].buy_orders.keys())
            best_ask = min(state.order_depths[product].sell_orders.keys())
            mids[product] = (best_bid + best_ask) / 2
        x = mids["COCONUT"] - 10000
        if x <= 0:
            regression_coeffs = [(34.08646745, 0.5302865), (56.67058553, 1.28420207), (16.60638543, 0.3410951)]
            prices = [x * a[1] + a[0] for a in regression_coeffs]
            return int(round(min(prices)+600)), int(round(max(prices)+600))
        if x > 0:
            regression_coeffs = [(51.9612041, 0.29568128), (24.64350008, 0.63945882)]
            prices = [x * a[1] + a[0] for a in regression_coeffs]
            return int(round(min(prices)+600)), int(round(max(prices)+600))

    # def order_coconut(self, state: TradingState):
    #     orders = []
    #     product = "COCONUT"
    #
    #     if product not in state.order_depths:
    #         return orders
    #
    #     pos = state.position.get(product, 0)
    #
    #     # best_bid = 0
    #     # best_ask = 0
    #     # if state.order_depths[product].sell_orders:
    #     #     best_ask = min(state.order_depths[product].sell_orders.keys())
    #     # if state.order_depths[product].buy_orders:
    #     #     best_bid = max(state.order_depths[product].buy_orders.keys())
    #
    #     coc_low, coc_high = self.eval_coconut(state)
    #
    #     q = self.limits[product] - pos
    #     buy_price = coc_low
    #     if q * pos < 0:
    #         buy_price -= self.coc_margin/3
    #     else:
    #         buy_price -= self.coc_margin
    #
    #     if q > 0:
    #         orders.append(Order(product, coc_low-self.coc_margin, q))
    #
    #     q = -self.limits[product] - pos
    #     sell_price = coc_high + self.coc_margin
    #     if q * pos < 0:
    #         sell_price += self.coc_margin/3
    #     else:
    #         sell_price += self.coc_margin
    #
    #     if q < 0:
    #         orders.append(Order(product, coc_high+self.coc_margin, q))
    #
    #     return orders
    #
    # def order_coupon(self, state: TradingState):
    #     orders = []
    #     product = "COCONUT_COUPON"
    #
    #     if product not in state.order_depths:
    #         return orders
    #
    #     pos = state.position.get(product, 0)
    #
    #     # best_bid = 0
    #     # best_ask = 0
    #     # if state.order_depths[product].sell_orders:
    #     #     best_ask = min(state.order_depths[product].sell_orders.keys())
    #     # if state.order_depths[product].buy_orders:
    #     #     best_bid = max(state.order_depths[product].buy_orders.keys())
    #
    #     coup_low, coup_high = self.eval_coupon(state)
    #
    #     q = self.limits[product] - pos
    #     buy_price = coup_low
    #     if q * pos < 0:
    #         buy_price -= self.coup_margin/3
    #     else:
    #         buy_price -= self.coup_margin
    #
    #     if q > 0:
    #         orders.append(Order(product, coup_low-self.coup_margin, q))
    #
    #     q = -self.limits[product] - pos
    #     sell_price = coup_high
    #     if q * pos < 0:
    #         sell_price += self.coup_margin/3
    #     else:
    #         sell_price += self.coup_margin
    #     if q < 0:
    #         orders.append(Order(product, coup_high+self.coup_margin, q))
    #
    #     return orders

    def order_spread(self, state: TradingState):

        orders = {"COCONUT": [], "COCONUT_COUPON": []}
        mids = {}
        for product in ["COCONUT", "COCONUT_COUPON"]:
            if len(state.order_depths[product].buy_orders) == 0 or len(state.order_depths[product].sell_orders) == 0:
                return orders
            best_bid = max(state.order_depths[product].buy_orders.keys())
            best_ask = min(state.order_depths[product].sell_orders.keys())
            mids[product] = (best_bid + best_ask) / 2

        # get mids diff
        # diff = {}
        # for product in ["COCONUT", "COCONUT_COUPON"]:
        # 	if self.coconut_prev_mids[product] is None:
        # 		self.coconut_prev_mids[product] = mids[product]
        # 		return orders
        # 	else:
        # 		diff[product] = mids[product] - self.coconut_prev_mids[product]
        # 		self.coconut_prev_mids[product] = mids[product]
        # spread = self.coconut_multipliers["COCONUT"] * diff["COCONUT"] + self.coconut_multipliers["COCONUT_COUPON"] * diff["COCONUT_COUPON"]
        spread = mids["COCONUT_COUPON"] * self.coconut_multipliers["COCONUT_COUPON"] + mids["COCONUT"] * \
                 self.coconut_multipliers["COCONUT"]
        self.coconut_spread_history.append(spread)
        self.coconut_spread_history = self.coconut_spread_history[-self.coconut_window:]
        if len(self.coconut_spread_history) < self.coconut_window * 0.5:
            return orders

        spread_value = spread - np.median(self.coconut_spread_history)
        if abs(spread_value) > self.coconut_spread_limit:
            print(f"Spread value: {spread_value} for time {state.timestamp}")

        if state.timestamp == 245000:
            print(f"Spread value: {spread_value} for time {state.timestamp}")
        current_n_spreads = state.position.get("COCONUT_COUPON", 0) / self.coconut_multipliers["COCONUT_COUPON"]
        if spread_value > self.coconut_spread_limit:
            self.target_n_spreads = -self.limits["COCONUT_COUPON"] / self.coconut_multipliers["COCONUT_COUPON"]
        elif spread_value < -self.coconut_spread_limit:
            self.target_n_spreads = int(self.limits["COCONUT_COUPON"] / self.coconut_multipliers["COCONUT_COUPON"])
        elif current_n_spreads * spread_value > 0:
            self.target_n_spreads = 0
        else:
            return orders

        target_n_spreads = self.target_n_spreads
        print(f"Current n_spreads: {current_n_spreads}, target n_spreads: {target_n_spreads}")

        if target_n_spreads < current_n_spreads:
            worst_bid_coupon = min(state.order_depths["COCONUT_COUPON"].buy_orders.keys())
            worst_ask_coconut = max(state.order_depths["COCONUT"].sell_orders.keys())
            # quantity to sell coupon
            q_coupon = calculate_sell_quantity(state.order_depths["COCONUT_COUPON"], worst_bid_coupon)
            q_coupon = max(q_coupon,
                           self.coconut_multipliers["COCONUT_COUPON"] * (target_n_spreads - current_n_spreads))
            # quantity to buy coconut
            q_coconut = calculate_buy_quantity(state.order_depths["COCONUT"], worst_ask_coconut)
            q_coconut = min(q_coconut, (target_n_spreads - current_n_spreads) * self.coconut_multipliers["COCONUT"])
            n_spreads = -min(abs(q_coupon / self.coconut_multipliers["COCONUT_COUPON"]),
                             abs(q_coconut / self.coconut_multipliers["COCONUT"]))
            # q_coconut = int(n_spreads*self.coconut_multipliers["COCONUT"])
            q_coconut = int(
                (current_n_spreads + n_spreads) * self.coconut_multipliers["COCONUT"] - state.position.get("COCONUT",
                                                                                                           0))
            q_coupon = int(n_spreads * self.coconut_multipliers["COCONUT_COUPON"])
            orders["COCONUT_COUPON"].append(Order("COCONUT_COUPON", worst_bid_coupon, q_coupon))
            orders["COCONUT"].append(Order("COCONUT", worst_ask_coconut, q_coconut))
        elif target_n_spreads > current_n_spreads:
            worst_ask_coupon = max(state.order_depths["COCONUT_COUPON"].sell_orders.keys())
            worst_bid_coconut = min(state.order_depths["COCONUT"].buy_orders.keys())
            # quantity to buy coupon
            q_coupon = calculate_buy_quantity(state.order_depths["COCONUT_COUPON"], worst_ask_coupon)
            q_coupon = min(q_coupon,
                           self.coconut_multipliers["COCONUT_COUPON"] * (target_n_spreads - current_n_spreads))
            # quantity to sell coconut
            q_coconut = calculate_sell_quantity(state.order_depths["COCONUT"], worst_bid_coconut)
            q_coconut = max(q_coconut, (target_n_spreads - current_n_spreads) * self.coconut_multipliers["COCONUT"])
            n_spreads = min(abs(q_coupon / self.coconut_multipliers["COCONUT_COUPON"]),
                            abs(q_coconut / self.coconut_multipliers["COCONUT"]))
            # q_coconut = int(n_spreads*self.coconut_multipliers["COCONUT"])
            q_coconut = int((current_n_spreads + n_spreads) * self.coconut_multipliers[
                "COCONUT"] - state.position.get("COCONUT", 0))
            q_coupon = int(n_spreads * self.coconut_multipliers["COCONUT_COUPON"])
            orders["COCONUT_COUPON"].append(Order("COCONUT_COUPON", worst_ask_coupon, q_coupon))
            orders["COCONUT"].append(Order("COCONUT", worst_bid_coconut, q_coconut))

        return orders


    def order_orchid(self, state: TradingState):
        product = "ORCHIDS"
        pos = state.position.get(product, 0)
        observation = state.observations.conversionObservations[product]

        print(f"OBSERVATION.askPrice: {observation.askPrice}")
        print(f"OBSERVATION.importTariff: {observation.importTariff}")
        print(f"OBSERVATION.transportFees: {observation.transportFees}")

        min_profitable_bid = round(
            observation.askPrice + observation.importTariff + observation.transportFees + self.min_bid_margin)

        q = calculate_sell_quantity(state.order_depths[product], min_profitable_bid)
        q = max(q, -self.limits[product] - pos)
        if q != 0:
            orders = [Order(product, min_profitable_bid, q)]
        else:
            orders = []

        # market making
        margin_values = list(range(0, 5))

        south_ask = observation.askPrice + observation.importTariff + observation.transportFees
        available_q = max(-self.limits[product] - pos - q, -self.limits[product])

        self.prev_south_ask = south_ask
        best_bid = max(state.order_depths[product].buy_orders.keys())
        self.prev_best_bid = best_bid

        print(f"South ask: {south_ask}")
        print(f"Best bid: {best_bid}")

        if available_q < -len(margin_values):
            for margin in margin_values:
                small_q = -1
                ask_price = self.get_orchid_price(south_ask, best_bid, margin)
                orders.append(Order(product, ask_price, small_q))
        else:
            return orders

        available_q += len(margin_values)

        if len(self.orchid_spreads) < 0.1 * self.orchid_window:
            ask_price = int((south_ask + 1.5))
            orders.append(Order(product, ask_price, available_q))
            return orders

        probs = []
        for margin in margin_values:
            prob = sum([1.0 for x in self.orchid_spreads if x[1] == margin]) / len(
                self.orchid_spreads)
            probs.append((margin, prob))

        def profit_for_margin(margin):
            return self.get_orchid_price(south_ask, best_bid, margin) - south_ask

        expected_profits = [(x, y, profit_for_margin(x) * y) for x, y in probs]
        best_margin = max(expected_profits, key=lambda x: x[2])[0]
        print(f"Best margin: {best_margin}")

        ask_price = self.get_orchid_price(south_ask, best_bid, best_margin)
        if available_q < 0:
            orders.append(Order(product, ask_price, available_q))

        return orders

    def update_limit_hits(self, state: TradingState):
        for product in self.products:
            if product in state.position and state.position[product] == self.limits[product]:
                self.limit_hits_up[product] += 1
            elif product in state.position and state.position[product] == -self.limits[product]:
                self.limit_hits_down[product] += 1
        if self.verbose:
            print(f"Limit hits up: {self.limit_hits_up}")
            print(f"Limit hits down: {self.limit_hits_down}")
        return self.limit_hits_up, self.limit_hits_down
