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
    current_deviation = deviation / 100.0  # decimal

    for _ in range(max_orders):
        current_price *= (1 - current_deviation)
        prices.append(round(current_price, 12))
        current_deviation *= step_multiplier
    return prices

def calc_averaging_order_sizes(avg_order_size: float, size_multiplier: float, max_orders: int = 6):
    return [round(avg_order_size * (size_multiplier ** i), 2) for i in range(max_orders)]


def weighted_average_price_and_units(entry_price: float,
                                     base_order_usd: float,
                                     avg_prices: list[float],
                                     avg_order_usd: list[float]):
    total_cost_usd = base_order_usd
    total_units = base_order_usd / entry_price

    for p, usd in zip(avg_prices, avg_order_usd):
        total_cost_usd += usd
        total_units += usd / p

    avg_price = total_cost_usd / total_units
    return avg_price, total_units

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

def tp_price_position_based(avg_entry_price: float, take_profit_pct: float) -> float:
    return avg_entry_price * (1 + take_profit_pct / 100.0)

def run_dca_backtest(backtest_config: BacktestConfig, bot_config: BotConfig) -> BacktestResult:
    assets = bot_config.assets
    current_balance = backtest_config.starting_balance
    total_profit_loss = 0.0
    trades: list[Trade] = []

    in_trade = False
    current_trade: Optional[Trade] = None
    current_tp_price: float = 0.0

    for asset in assets:
        df = data.get_df(asset=asset)
        df = df.loc[
            (df["timestamp"] >= backtest_config.start_date)
            & (df["timestamp"] <= backtest_config.end_date)
        ]

        # Faster iteration
        for row in df.itertuples(index=False):
            row_open = row.open
            row_high = row.high
            row_low  = row.low
            row_time = row.timestamp

            if in_trade:
                if row_high >= current_tp_price:
                    filled_prices = current_trade.avg_orders_prices[:current_trade.avg_orders_filled]
                    filled_usd    = current_trade.avg_orders_sizes[:current_trade.avg_orders_filled]

                    avg_price, total_units = weighted_average_price_and_units(
                        entry_price=current_trade.entry_price,
                        base_order_usd=current_trade.base_order_size,
                        avg_prices=filled_prices,
                        avg_order_usd=filled_usd,
                    )

                    profit_loss = total_units * (current_tp_price - avg_price)

                    bot_config.reinvest_profit(profit_loss)

                    current_balance += profit_loss
                    total_profit_loss += profit_loss

                    current_trade.avg_entry_price = avg_price
                    current_trade.profit_loss = profit_loss
                    current_trade.close_datetime = row_time
                    current_trade.close_price = current_tp_price

                    trades.append(current_trade)
                    current_trade = None
                    in_trade = False
                    continue
                if current_trade.avg_orders_filled < bot_config.max_averaging_orders:
                    idx = current_trade.avg_orders_filled
                    next_price = current_trade.avg_orders_prices[idx]
                    if row_low <= next_price:
                        new_usd = current_trade.avg_orders_sizes[idx]
                        current_trade.total_order_size += new_usd
                        current_trade.avg_orders_filled += 1

                        filled_prices = current_trade.avg_orders_prices[:current_trade.avg_orders_filled]
                        filled_usd    = current_trade.avg_orders_sizes[:current_trade.avg_orders_filled]

                        avg_price, total_units = weighted_average_price_and_units(
                            entry_price=current_trade.entry_price,
                            base_order_usd=current_trade.base_order_size,
                            avg_prices=filled_prices,
                            avg_order_usd=filled_usd,
                        )
                        current_trade.avg_entry_price = avg_price
                        current_tp_price = tp_price_position_based(
                            current_trade.avg_entry_price, bot_config.take_profit
                        )
                        current_trade.take_profit_levels.append(current_tp_price)

            else:
                current_trade = open_trade(asset, row, bot_config)

                current_tp_price = tp_price_position_based(
                    current_trade.entry_price, bot_config.take_profit
                )
                current_trade.take_profit_levels.append(current_tp_price)
                in_trade = True

        result = BacktestResult(
            asset=asset,
            trades=trades,
            ending_balance=round(current_balance, 2),
            gain_loss=round(total_profit_loss, 2),
            percent_gain_loss=round(
                ((current_balance - backtest_config.starting_balance) / backtest_config.starting_balance) * 100.0, 2
            ),
        )

    return result


