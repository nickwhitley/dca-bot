from statistics import mean
from typing import Optional

import pandas as pd
from backtesting.backtest_result import BacktestResult
from constants import Asset
from bot.bot_config import BotConfig
from backtesting.backtest_config import BacktestConfig

from datetime import datetime
from data import data
from models.trade import Trade

def calc_averaging_order_prices(initial_price: float, deviation: float, step_multiplier: float, max_orders: int = 6):
    prices = []
    current_price = initial_price
    current_deviation = deviation / 100  # convert to decimal

    for i in range(max_orders):
        current_price *= (1 - current_deviation)
        prices.append(round(current_price, 12))
        current_deviation *= step_multiplier  # increase step for next order

    return prices

def calc_averaging_order_sizes(avg_order_size: float, size_multiplier: float):
     sizes = [
          round(avg_order_size * (size_multiplier ** i), 2)
          for i in range(6)
     ]
     return sizes

def weighted_average_price(entry_price, base_order_size, avg_prices, avg_order_size):
    total_cost = entry_price * base_order_size

    for price, qty in zip(avg_prices, avg_order_size):
        total_cost += price * qty
        base_order_size += qty

    return total_cost / base_order_size

def open_trade(asset: Asset, row: pd.Series, bot_config: BotConfig) -> Trade:
    return Trade(
        asset=asset,
        entry_price=row.open,
        entry_datetime=row.timestamp,
        base_order_size=bot_config.base_order_size,
        total_order_size=bot_config.base_order_size,
        avg_orders_prices=calc_averaging_order_prices(
             initial_price=row.open,
             deviation=bot_config.price_deviation,
             step_multiplier=bot_config.averaging_order_step_multiplier
        ),
        avg_orders_sizes=calc_averaging_order_sizes(
             avg_order_size=bot_config.averaging_order_size,
             size_multiplier=bot_config.averaging_order_size_multiplier
        ),
        avg_entry_price=row.open
    )

def calculate_tp_price(entry_price, order_size, take_profit) -> float:
    target_profit = order_size * (take_profit / 100)
    quantity_bought = order_size / entry_price
    profit_per_unit = target_profit / quantity_bought
    current_tp_price = entry_price + profit_per_unit
    return current_tp_price
    

def run_dca_backtest(backtest_config: BacktestConfig, bot_config: BotConfig) -> BacktestResult:
    assets = bot_config.assets
    current_balance = backtest_config.starting_balance
    total_profit_loss = 0
    trades: list[Trade] = []
    drawdowns: list[float] = []

    in_trade = False
    current_trade: Optional[Trade] = None
    current_tp_price: float = None
    max_drawdown = 0
    trade_drawdown = 0

    for asset in assets:
        df = data.get_df(asset=asset)
        print(backtest_config.start_date)
        print(backtest_config.end_date)
        print("First row:", df.head(1)["timestamp"].values[0])
        print("Last row:", df.tail(1)["timestamp"].values[0])
        df = df.loc[
            (df["timestamp"] >= backtest_config.start_date)
            & (df["timestamp"] <= backtest_config.end_date)
        ]
        print("First row:", df.head(1)["timestamp"].values[0])
        print("Last row:", df.tail(1)["timestamp"].values[0])

        for _, row in enumerate(df.itertuples(), 0):
            if in_trade:
                avg_orders_index = current_trade.avg_orders_filled
                closest_avg_order_price = current_trade.avg_orders_prices[avg_orders_index]
                # trade hit tp - closing
                if row.high >= current_tp_price:
                    # TODO: Profit loss is broken
                    profit_loss = current_trade.total_order_size * (current_tp_price - current_trade.avg_entry_price)
                    current_balance += profit_loss
                    total_profit_loss += profit_loss
                    current_trade.profit_loss = profit_loss
                    current_trade.close_datetime = row.timestamp
                    current_trade.close_price = current_tp_price
                    trades.append(current_trade)
                    current_trade = None
                    in_trade = False
                    drawdowns.append(trade_drawdown)
                    trade_drawdown = 0
                # trade hit averaging price - averaging down
                elif row.low <= closest_avg_order_price and current_trade.avg_orders_filled < bot_config.max_averaging_orders - 1:
                    
                    new_qty = current_trade.avg_orders_sizes[avg_orders_index]
                    current_trade.total_order_size += new_qty
                    current_trade.avg_orders_filled += 1

                    filled_prices = current_trade.avg_orders_prices[:current_trade.avg_orders_filled]
                    filled_balances = current_trade.avg_orders_sizes[:current_trade.avg_orders_filled]

                    average_entry_price = weighted_average_price(
                        entry_price=current_trade.entry_price,
                        base_order_size=current_trade.base_order_size,
                        avg_prices=filled_prices,
                        avg_order_size=filled_balances
                    )

                    current_trade.avg_entry_price = average_entry_price
                    current_tp_price = calculate_tp_price(
                        entry_price=current_trade.avg_entry_price,
                        order_size=current_trade.total_order_size,
                        take_profit=bot_config.take_profit
                    )
                    current_trade.take_profit_levels.append(current_tp_price)
                    
            # opening trade
            elif not in_trade:
                current_trade = open_trade(asset, row, bot_config)
                current_tp_price = calculate_tp_price(
                    entry_price=current_trade.entry_price,
                    order_size=current_trade.total_order_size,
                    take_profit=bot_config.take_profit
                )
                current_trade.take_profit_levels.append(current_tp_price)
                in_trade = True
    
    result = BacktestResult(
        trades=trades,
        ending_balance=current_balance,
        max_drawdown=max_drawdown,
        average_drawdown=mean(drawdowns),
        gain_loss=total_profit_loss,
        percent_gain_loss = ((current_balance - backtest_config.starting_balance) 
                     / backtest_config.starting_balance) * 100
    )

    return result


