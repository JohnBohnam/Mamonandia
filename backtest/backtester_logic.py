# from one_day_Trader import Trader
from plotters import Plotter
from datamodel import *
import pandas as pd
import statistics
import copy
import os

from consts import *

# from Strategy2023.trader import Trader
from stupidon import Trader
from backtester_logging import create_log_file


def process_prices(df_prices, round_, time_limit) -> dict[int, TradingState]:
    states = {}
    for _, row in df_prices.iterrows():
        time: int = int(row["timestamp"])
        if time > time_limit:
            break
        product: str = row["product"]
        if states.get(time) == None:
            position: Dict[Product, Position] = {}
            own_trades: Dict[Symbol, List[Trade]] = {}
            market_trades: Dict[Symbol, List[Trade]] = {}
            observations: Dict[Product, Observation] = {}
            listings = {}
            depths = {}
            states[time] = TradingState(time, listings, depths, own_trades, market_trades, position,
                                        observations)

        if product not in states[time].position and product in SYMBOLS_BY_ROUND_POSITIONABLE[round_]:
            states[time].position[product] = 0
            states[time].own_trades[product] = []
            states[time].market_trades[product] = []

        states[time].listings[product] = Listing(product, product, "1")

        if product == "DOLPHIN_SIGHTINGS":
            states[time].observations["DOLPHIN_SIGHTINGS"] = row['mid_price']

        depth = OrderDepth()
        if row["bid_price_1"] > 0:
            depth.buy_orders[row["bid_price_1"]] = int(row["bid_volume_1"])
        if row["bid_price_2"] > 0:
            depth.buy_orders[row["bid_price_2"]] = int(row["bid_volume_2"])
        if row["bid_price_3"] > 0:
            depth.buy_orders[row["bid_price_3"]] = int(row["bid_volume_3"])
        if row["ask_price_1"] > 0:
            depth.sell_orders[row["ask_price_1"]] = -int(row["ask_volume_1"])
        if row["ask_price_2"] > 0:
            depth.sell_orders[row["ask_price_2"]] = -int(row["ask_volume_2"])
        if row["ask_price_3"] > 0:
            depth.sell_orders[row["ask_price_3"]] = -int(row["ask_volume_3"])
        states[time].order_depths[product] = depth

    return states


def process_trades(df_trades, states: dict[int, TradingState], time_limit, names=True):
    '''
    add trades to the book orders. No order exercise included
    :param df_trades:
    :param states:
    :param time_limit:
    :param names:
    :return:
    '''
    for _, trade in df_trades.iterrows():
        time: int = trade['timestamp']
        if time > time_limit:
            break
        symbol = trade['symbol']
        if symbol not in states[time].market_trades:
            states[time].market_trades[symbol] = []
        t = Trade(
            symbol,
            trade['price'],
            trade['quantity'],
            str(trade['buyer']),
            str(trade['seller']),
            time)
        states[time].market_trades[symbol].append(t)
    return states


def calc_mid(states: dict[int, TradingState], round_: int, time: int, max_time: int) -> dict[
    str, float]:
    medians_by_symbol = {}
    non_empty_time = time

    for psymbol in SYMBOLS_BY_ROUND_POSITIONABLE[round_]:
        hitted_zero = False
        while len(states[non_empty_time].order_depths[psymbol].sell_orders.keys()) == 0 or len(
                states[non_empty_time].order_depths[psymbol].buy_orders.keys()) == 0:
            # little hack
            if time == 0 or hitted_zero and time != max_time:
                hitted_zero = True
                non_empty_time += TIME_DELTA
            else:
                non_empty_time -= TIME_DELTA
        min_ask = min(states[non_empty_time].order_depths[psymbol].sell_orders.keys())
        max_bid = max(states[non_empty_time].order_depths[psymbol].buy_orders.keys())
        median_price = statistics.median([min_ask, max_bid])
        medians_by_symbol[psymbol] = median_price
    return medians_by_symbol


# Setting a high time_limit can be harder to visualize
# print_position prints the position before! every Trader.run
def simulate_alternative(
        round_: int,
        day: int,
        trader,
        time_limit=999900,
        names=True,
        halfway=False,
        logging=True,
        plotting=True,
        verbose=True,
        df_prices=None,  # df can be passed to avoid reading from file
        df_trades=None,  # df can be passed to avoid reading from file
):
    '''main function that parse trades from csv and runs the simulation. After that runs plots and visualize them'''

    if df_prices is None:
        prices_path = os.path.join(TRAINING_DATA_PREFIX, f'prices_round_{round_}_day_{day}.csv')
        df_prices = pd.read_csv(prices_path, sep=';')

    if df_trades is None:
        trades_path = os.path.join(TRAINING_DATA_PREFIX, f'trades_round_{round_}_day_{day}_wn.csv')
        if not names:
            trades_path = os.path.join(TRAINING_DATA_PREFIX, f'trades_round_{round_}_day_{day}_nn.csv')
        df_trades = pd.read_csv(trades_path, sep=';', dtype={'seller': str, 'buyer': str})

    states = process_prices(df_prices, round_, time_limit)
    states = process_trades(df_trades, states, time_limit, names)
    ref_symbols = list(states[0].position.keys())
    max_time = max(list(states.keys()))

    # handling these four is rather tricky
    profits_by_symbol: dict[int, dict[str, float]] = {
        0: dict(zip(ref_symbols, [0.0] * len(ref_symbols)))
    }
    balance_by_symbol: dict[int, dict[str, float]] = {0: copy.deepcopy(profits_by_symbol[0])}
    credit_by_symbol: dict[int, dict[str, float]] = {0: copy.deepcopy(profits_by_symbol[0])}
    unrealized_by_symbol: dict[int, dict[str, float]] = {0: copy.deepcopy(profits_by_symbol[0])}

    states, profits_by_symbol, balance_by_symbol = trades_position_pnl_run(states, max_time, trader,
                                                                           profits_by_symbol,
                                                                           balance_by_symbol,
                                                                           credit_by_symbol,
                                                                           unrealized_by_symbol,
                                                                           round_,
                                                                           halfway=halfway,
                                                                           verbose=verbose)
    if logging:
        create_log_file(round_, day, states, profits_by_symbol, balance_by_symbol, trader)
    if plotting:
        kwargs = {
            "states": states,
            "trader": trader,
            "profits_by_symbol": profits_by_symbol,
            "balance_by_symbol": balance_by_symbol,
            "old": old,
        }
        plotter = Plotter(SYMBOLS_BY_ROUND_POSITIONABLE[round_], **kwargs)
        plotter.plot_stats()
    res = {}
    for symbol in SYMBOLS_BY_ROUND_POSITIONABLE[round_]:
        res[symbol] = profits_by_symbol[max_time][symbol] + balance_by_symbol[max_time][symbol] # ??
    return res


def trades_position_pnl_run(
        states: dict[int, TradingState],
        max_time: int,
        trader: Trader,
        profits_by_symbol: dict[int, dict[str, float]],
        balance_by_symbol: dict[int, dict[str, float]],
        credit_by_symbol: dict[int, dict[str, float]],
        unrealized_by_symbol: dict[int, dict[str, float]],
        round_,
        halfway=False,
        verbose=True,
):
    spent_buy = 0  # variable is useless, only double check the profits in the end
    spent_sell = 0
    for time, state in states.items():
        position = copy.deepcopy(state.position)
        if old:
            orders = trader.run(state)
        else:
            orders, _, _ = trader.run(state)
        trades = clear_order_book(orders, state.order_depths, time, halfway)
        mids = calc_mid(states, round_, time, max_time)
        if time != max_time:
            profits_by_symbol[time + TIME_DELTA] = copy.deepcopy(profits_by_symbol[time])
            credit_by_symbol[time + TIME_DELTA] = copy.deepcopy(credit_by_symbol[time])
            balance_by_symbol[time + TIME_DELTA] = copy.deepcopy(balance_by_symbol[time])
            unrealized_by_symbol[time + TIME_DELTA] = copy.deepcopy(unrealized_by_symbol[time])
            for psymbol in SYMBOLS_BY_ROUND_POSITIONABLE[round_]:
                unrealized_by_symbol[time + TIME_DELTA][psymbol] = mids[psymbol] * position[psymbol]

        valid_trades = []
        grouped_by_symbol = {}
        if len(trades) > 0:
            for trade in trades:
                n_position = position[trade.symbol] + trade.quantity
                if abs(n_position) > current_limits[trade.symbol]:
                    if verbose:
                        print(trade.__dict__)
                        raise ValueError(
                            'ILLEGAL TRADE, WOULD EXCEED POSITION LIMIT, KILLING ALL REMAINING ORDERS')

                else:
                    valid_trades.append(trade)

        FLEX_TIME_DELTA = TIME_DELTA
        if time == max_time:
            FLEX_TIME_DELTA = 0
        for valid_trade in valid_trades:
            if grouped_by_symbol.get(valid_trade.symbol) == None:
                grouped_by_symbol[valid_trade.symbol] = []
            grouped_by_symbol[valid_trade.symbol].append(valid_trade)
            if valid_trade.quantity > 0:
                spent_buy += trade.price * trade.quantity
            else:
                spent_sell += -trade.price * trade.quantity

            new_credit, profit = calculate_credit_and_profit(valid_trade,
                                                             position[valid_trade.symbol],
                                                             credit_by_symbol[
                                                                 time + FLEX_TIME_DELTA][
                                                                 valid_trade.symbol])
            profits_by_symbol[time + FLEX_TIME_DELTA][valid_trade.symbol] += profit
            credit_by_symbol[time + FLEX_TIME_DELTA][valid_trade.symbol] = new_credit
            position[trade.symbol] += valid_trade.quantity
        print(f"time: {time}, position: {position}")
        print("valid trades")
        for trade in valid_trades:
            print(trade.__dict__)
        if states.get(time + FLEX_TIME_DELTA) != None:
            states[time + FLEX_TIME_DELTA].own_trades = grouped_by_symbol
        for psymbol in SYMBOLS_BY_ROUND_POSITIONABLE[round_]:
            unrealized_by_symbol[time + FLEX_TIME_DELTA][psymbol] = mids[psymbol] * position[
                psymbol]
            balance_by_symbol[time + FLEX_TIME_DELTA][psymbol] = \
                credit_by_symbol[time + FLEX_TIME_DELTA][psymbol] + \
                unrealized_by_symbol[time + FLEX_TIME_DELTA][psymbol]

        if time == max_time:
            if verbose:
                print("End of simulation reached. All positions left are liquidated")
            # i have the feeling this already has been done, and only repeats the same values as before
            for osymbol in position.keys():
                profits_by_symbol[time + FLEX_TIME_DELTA][osymbol] += \
                    unrealized_by_symbol[time + FLEX_TIME_DELTA][osymbol] + \
                    credit_by_symbol[time + FLEX_TIME_DELTA][osymbol]
                balance_by_symbol[time + FLEX_TIME_DELTA][osymbol] = 0
                if position[osymbol] > 0:
                    spent_sell += mids[osymbol] * position[osymbol]
                else:
                    spent_buy += -mids[osymbol] * position[osymbol]

        if states.get(time + FLEX_TIME_DELTA) != None:
            states[time + FLEX_TIME_DELTA].position = copy.deepcopy(position)
        if verbose and trades:
            print(f'Trades at time {time}: {[x.__dict__ for x in trades]}')
            print(f"Profits after time {time}: {profits_by_symbol[time + TIME_DELTA]}")
    if verbose:
        print(
            f"spent_buy: {spent_buy}, spent_sell: {spent_sell}, spent_sell - spent_buy: {spent_sell - spent_buy}")
    return states, profits_by_symbol, balance_by_symbol


def cleanup_order_volumes(org_orders: List[Order]) -> List[Order]:
    orders = []
    for order_1 in org_orders:
        final_order = copy.copy(order_1)
        for order_2 in org_orders:
            if order_1.price == order_2.price and order_1.quantity == order_2.quantity:
                continue
            if order_1.price == order_2.price:
                final_order.quantity += order_2.quantity
        orders.append(final_order)
    return orders


def clear_order_book(trader_orders: dict[str, List[Order]], order_depth: dict[str, OrderDepth],
                     time: int, halfway: bool) -> list[Trade]:
    trades = []
    for symbol in trader_orders.keys():
        if order_depth.get(symbol) != None:
            symbol_order_depth = copy.deepcopy(order_depth[symbol])
            t_orders = cleanup_order_volumes(trader_orders[symbol])
            for order in t_orders:
                if order.quantity < 0:
                    if halfway:
                        bids = symbol_order_depth.buy_orders.keys()
                        asks = symbol_order_depth.sell_orders.keys()
                        max_bid = max(bids)
                        min_ask = min(asks)
                        if order.price <= statistics.median([max_bid, min_ask]):
                            trades.append(
                                Trade(symbol, order.price, order.quantity, "BOT", "YOU", time))
                    # else:
                    # print(f'No matches for order {order} at time {time}')
                    # print(f'Order depth is {order_depth[order.symbol].__dict__}')
                    else:
                        potential_matches = list(filter(lambda o: o[0] == order.price,
                                                        symbol_order_depth.buy_orders.items()))
                        if len(potential_matches) > 0:
                            match = potential_matches[0]
                            final_volume = 0
                            if abs(match[1]) > abs(order.quantity):
                                final_volume = order.quantity
                            else:
                                # this should be negative
                                final_volume = -match[1]
                            trades.append(
                                Trade(symbol, order.price, final_volume, "BOT", "YOU", time))
                    # else:
                    # print(f'No matches for order {order} at time {time}')
                    # print(f'Order depth is {order_depth[order.symbol].__dict__}')
                if order.quantity > 0:
                    if halfway:
                        bids = symbol_order_depth.buy_orders.keys()
                        asks = symbol_order_depth.sell_orders.keys()
                        max_bid = max(bids)
                        min_ask = min(asks)
                        if order.price >= statistics.median([max_bid, min_ask]):
                            trades.append(
                                Trade(symbol, order.price, order.quantity, "YOU", "BOT", time))
                    # else:
                    #     print(f'No matches for order {order} at time {time}')
                    #     print(f'Order depth is {order_depth[order.symbol].__dict__}')
                    else:
                        potential_matches = list(filter(lambda o: o[0] == order.price,
                                                        symbol_order_depth.sell_orders.items()))
                        if len(potential_matches) > 0:
                            match = potential_matches[0]
                            final_volume = 0
                            # Match[1] will be negative so needs to be changed to work here
                            if abs(match[1]) > abs(order.quantity):
                                final_volume = order.quantity
                            else:
                                final_volume = abs(match[1])
                            trades.append(
                                Trade(symbol, order.price, final_volume, "YOU", "BOT", time))
                    # else:
                    #     print(f'No matches for order {order} at time {time}')
                    #     print(f'Order depth is {order_depth[order.symbol].__dict__}')
    return trades


def calculate_credit_and_profit(trade, position, credit):
    if trade.quantity * position >= 0:
        credit -= trade.quantity * trade.price
        profit = 0
        return credit, profit
    else:
        if abs(trade.quantity) <= abs(position):
            # we sold/bought less than we had
            avg_price = abs(credit) / abs(position)
            profit = (trade.price - avg_price) * (-trade.quantity)
            credit -= trade.quantity * avg_price
            return credit, profit
        else:
            # we sold/bought everything and have new position
            avg_price = abs(credit) / abs(position)
            profit = (trade.price - avg_price) * (position)
            credit = -trade.price * (
                    trade.quantity + position)  # trade quantity and position are different signs
            return credit, profit
