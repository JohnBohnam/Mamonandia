# from one_day_Trader import Trader
from plotters import Plotter
# from Strategy2023.trader import Trader
from datamodel import *
import pandas as pd
import statistics
import copy
import uuid
import os
from datetime import datetime

from consts import *


csv_header = "day;timestamp;product;bid_price_1;bid_volume_1;bid_price_2;bid_volume_2;bid_price_3;bid_volume_3;ask_price_1;ask_volume_1;ask_price_2;ask_volume_2;ask_price_3;ask_volume_3;mid_price;profit_and_loss\n"
log_header = [
    'Sandbox logs:\n',
    '0 OpenBLAS WARNING - could not determine the L2 cache size on this system, assuming 256k\n',
    'START RequestId: 8ab36ff8-b4e6-42d4-b012-e6ad69c42085 Version: $LATEST\n',
    'END RequestId: 8ab36ff8-b4e6-42d4-b012-e6ad69c42085\n',
    'REPORT RequestId: 8ab36ff8-b4e6-42d4-b012-e6ad69c42085	Duration: 18.73 ms	Billed Duration: 19 ms	Memory Size: 128 MB	Max Memory Used: 94 MB	Init Duration: 1574.09 ms\n',
]


def create_log_file(round: int, day: int, states: dict[int, TradingState],
                    profits_by_symbol: dict[int, dict[str, float]],
                    balance_by_symbol: dict[int, dict[str, float]], trader):
    file_name = uuid.uuid4()
    timest = datetime.timestamp(datetime.now())
    max_time = max(list(states.keys()))
    log_path = os.path.join('logs', f'{timest}_{file_name}.log')
    if not os.path.exists('logs'):
        os.makedirs('logs')
    with open(log_path, mode='w', encoding="utf-8", newline='\n') as f:
        f.writelines(log_header)
        f.write('\n')
        for time, state in states.items():
            if hasattr(trader, 'logger'):
                if hasattr(trader.logger, 'local_logs') != None:
                    if trader.logger.local_logs.get(time) != None:
                        f.write(f'{time} {trader.logger.local_logs[time]}\n')
                        continue
            if time != 0:
                f.write(f'{time}\n')

        f.write(f'\n\n')
        f.write('Submission logs:\n\n\n')
        f.write('Activities log:\n')
        f.write(csv_header)
        for time, state in states.items():
            for symbol in SYMBOLS_BY_ROUND[round]:
                f.write(f'{day};{time};{symbol};')
                bids_length = len(state.order_depths[symbol].buy_orders)
                bids = list(state.order_depths[symbol].buy_orders.items())
                bids_prices = list(state.order_depths[symbol].buy_orders.keys())
                bids_prices.sort()
                asks_length = len(state.order_depths[symbol].sell_orders)
                asks_prices = list(state.order_depths[symbol].sell_orders.keys())
                asks_prices.sort()
                asks = list(state.order_depths[symbol].sell_orders.items())
                if bids_length >= 3:
                    f.write(
                        f'{bids[0][0]};{bids[0][1]};{bids[1][0]};{bids[1][1]};{bids[2][0]};{bids[2][1]};')
                elif bids_length == 2:
                    f.write(f'{bids[0][0]};{bids[0][1]};{bids[1][0]};{bids[1][1]};;;')
                elif bids_length == 1:
                    f.write(f'{bids[0][0]};{bids[0][1]};;;;;')
                else:
                    f.write(f';;;;;;')
                if asks_length >= 3:
                    f.write(
                        f'{asks[0][0]};{asks[0][1]};{asks[1][0]};{asks[1][1]};{asks[2][0]};{asks[2][1]};')
                elif asks_length == 2:
                    f.write(f'{asks[0][0]};{asks[0][1]};{asks[1][0]};{asks[1][1]};;;')
                elif asks_length == 1:
                    f.write(f'{asks[0][0]};{asks[0][1]};;;;;')
                else:
                    f.write(f';;;;;;')
                if len(asks_prices) == 0 or max(bids_prices) == 0:
                    if symbol == 'DOLPHIN_SIGHTINGS':
                        dolphin_sightings = state.observations['DOLPHIN_SIGHTINGS']
                        f.write(f'{dolphin_sightings};{0.0}\n')
                    else:
                        f.write(f'{0};{0.0}\n')
                else:
                    actual_profit = 0.0
                    if symbol in SYMBOLS_BY_ROUND_POSITIONABLE[round]:
                        actual_profit = profits_by_symbol[time][symbol] + balance_by_symbol[time][
                            symbol]
                    min_ask = min(asks_prices)
                    max_bid = max(bids_prices)
                    median_price = statistics.median([min_ask, max_bid])
                    f.write(f'{median_price};{actual_profit}\n')
                    if time == max_time:
                        if profits_by_symbol[time].get(symbol) != None:
                            print(f'Final profit for {symbol} = {actual_profit}')
        print(f"\nSimulation on round {round} day {day} for time {max_time} complete")

