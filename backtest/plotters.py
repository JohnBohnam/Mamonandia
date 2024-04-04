import matplotlib.pyplot as plt
from datamodel import *


class Plotter:
    '''
	prepare stats based on the states, trader, profits_by_symbol, balance_by_symbol
	the stats_dict is of the form {title: (x, {label: y})} OR {title: (x, y)}
	'''

    def __init__(self, symbols, states, trader, profits_by_symbol, balance_by_symbol):
        '''
		:param symbols: [str]
		:param states: dict[timestamp, TradingState]
		:param trader: Trader
		:param profits_by_symbol:dict[timestamp, dict[symbol, value]]
		:param balance_by_symbol: dict[timestamp, dict[symbol, potential_profit]]
		'''
        self.symbols = symbols
        self.states = states
        self.trader = trader
        self.profits_by_symbol = profits_by_symbol
        self.balance_by_symbol = balance_by_symbol
        self.stats_dict = {
            "Profit by symbol": self.get_profits_per_product(),
            "Exposure by symbol": self.get_balance_per_product(),
            "Position by symbol": self.get_position_per_product(),
        }

    def get_profits_per_product(self):
        profits_by_symbol = self.profits_by_symbol
        result = {}
        for symbol in self.symbols:
            timestamps = profits_by_symbol.keys()
            profits = [profits_by_symbol[ts][symbol] for ts in timestamps]
            result[symbol] = profits
        return (timestamps, result)

    def get_balance_per_product(self):
        balance_by_symbol = self.balance_by_symbol
        result = {}
        for symbol in self.symbols:
            timestamps = balance_by_symbol.keys()
            balances = [balance_by_symbol[ts][symbol] for ts in timestamps]
            result[symbol] = balances
        return (timestamps, result)

    def get_position_per_product(self):
        states = self.states
        result = {}
        for symbol in self.symbols:
            timestamps = states.keys()
            positions = [states[ts].position[symbol] for ts in timestamps]
            result[symbol] = positions
        return (timestamps, result)

    def get_bids(self):
        states = self.states
        result = {}
        for symbol in self.symbols:
            result[symbol] = {}
            timestamps = states.keys()
            for ts in timestamps:
                bids = states[ts].order_depths[symbol].buy_orders
                result[symbol][ts] = bids
        return result

    def get_asks(self):
        states = self.states
        result = {}
        for symbol in self.symbols:
            result[symbol] = {}
            timestamps = states.keys()
            for ts in timestamps:
                asks = states[ts].order_depths[symbol].sell_orders
                result[symbol][ts] = asks
        return result

    def get_trades_done(self):
        timestamps = self.states.keys()
        buys = {}
        sells = {}
        for symbol in self.symbols:
            buys[symbol] = []
            sells[symbol] = []
            for t, state in self.states.items():
                if symbol not in state.own_trades:
                    continue
                for trade in state.own_trades[symbol]:
                    # print(f"buyer: {trade.buyer}, seller: {trade.seller}")
                    if trade.buyer == "YOU":
                        buys[symbol].append((t, trade.price, trade.quantity))
                    if trade.seller == "YOU":
                        sells[symbol].append((t, trade.price, trade.quantity))
        return buys, sells

    # dict for the plot, key is title, value is a function that can take any of states, trader, profits_by_symbol, balance_by_symbol
    def plot_stats(self):
        num_plots = len(self.stats_dict)
        num_plots += 1
        fig, axes = plt.subplots(1, num_plots, figsize=(6 * num_plots, 6))

        for i, (title, stats) in enumerate(self.stats_dict.items()):
            ax = axes[i]
            if type(stats[1]) != dict:
                x, y = stats
                ax.plot(x, y)
            else:
                x = stats[0]
                for label, y in stats[1].items():
                    ax.plot(x, y, label=label)
            ax.set_title(title)
            ax.legend()
        # plot the trades
        ax = axes[-1]
        buys, sells = self.get_trades_done()
        asks = self.get_asks()
        bids = self.get_bids()
        for symbol in self.symbols:

            if symbol != "BANANAS":
                continue
            # sell_t, sell_p, sell_q = zip(*sells[symbol])
            # this does not work, idk why, python dumb
            sts = []
            sps = []
            sqs = []
            for t, p, q in sells[symbol]:
                sts.append(t)
                sps.append(p)
                sqs.append(q)

            plt.scatter(sts, sps, color="red")

            bts = []
            bps = []
            bqs = []
            for t, p, q in buys[symbol]:
                bts.append(t)
                bps.append(p)
                bqs.append(q)

            plt.scatter(bts, bps, color="blue")

            # print(self.get_asks()[symbol])
            best_asks = {}
            for timestamp, act_asks in asks[symbol].items():
                if len(act_asks) > 0:
                    best_asks[timestamp] = list(act_asks.keys())[0]

            best_bids = {}
            for timestamp, act_bids in bids[symbol].items():
                if len(act_bids) > 0:
                    best_bids[timestamp] = list(act_bids.keys())[-1]
                    print(best_bids[timestamp])


            ax.plot(best_asks.keys(), best_asks.values(), label="best ask", color="lightblue")
            ax.plot(best_bids.keys(), best_bids.values(), label='best_bid', color="orange")
            ax.legend()

        plt.tight_layout()
        plt.show()
