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

def calc_averaging_order_quantities(avg_order_size: float, size_multiplier: float):
     sizes = [
          round(avg_order_size * (size_multiplier ** i), 2)
          for i in range(6)
     ]
     return sizes

def weighted_average_price(entry_price, base_quantity, avg_prices, avg_quantities):
    total_cost = entry_price * base_quantity
    total_quantity = base_quantity

    for price, qty in zip(avg_prices, avg_quantities):
        total_cost += price * qty
        total_quantity += qty

    return total_cost / total_quantity

def open_trade(asset: Asset, row: pd.Series, bot_config: BotConfig) -> Trade:
    return Trade(
        asset=asset,
        entry_price=row.open,
        entry_datetime=row.timestamp,
        base_quantity=bot_config.base_order_size,
        total_quantity=bot_config.base_order_size,
        avg_orders_prices=calc_averaging_order_prices(
             initial_price=row.open,
             deviation=bot_config.price_deviation,
             step_multiplier=bot_config.averaging_order_step_multiplier
        ),
        avg_orders_quantities=calc_averaging_order_quantities(
             avg_order_size=bot_config.averaging_order_size,
             size_multiplier=bot_config.averaging_order_size_multiplier
        )
    )
    

def run_dca_backtest(backtest_config: BacktestConfig, bot_config: BotConfig) -> BacktestResult:
    assets = bot_config.assets
    current_balance = backtest_config.starting_balance
    current_profit_loss = 0
    trades: list[Trade] = []

    in_trade = False
    current_trade: Optional[Trade] = None
    current_tp_price: float = None

    

    for asset in assets:
        df = data.get_df(asset=asset)
        df = df.loc[
            (df["timestamp"] >= backtest_config.start_date)
            & (df["timestamp"] <= backtest_config.end_date)
        ]
        print(df)

        for index, row in enumerate(df.itertuples(), 0):
            if in_trade:
                avg_orders_index = current_trade.avg_orders_filled
                closest_avg_order_price = current_trade.avg_orders_prices[avg_orders_index]

                if row.open <= current_tp_price <= row.high and row.low > closest_avg_order_price:
                    profit_loss = current_trade.total_quantity * current_tp_price
                    current_balance += profit_loss
                    current_profit_loss += profit_loss
                    current_trade.profit_loss = current_profit_loss
                    current_trade.close_datetime = row.timestamp
                    current_trade.close_price = current_tp_price
                    trades.append(current_trade)
                    current_trade = None
                    in_trade = False
                elif row.low <= closest_avg_order_price <= row.close and current_trade.avg_orders_filled < bot_config.max_averaging_orders:
                    current_trade.total_quantity += current_trade.avg_orders_quantities[avg_orders_index]
                    filled_prices = current_trade.avg_orders_prices[:current_trade.avg_orders_filled-1]
                    filled_quantities = current_trade.avg_orders_quantities[:current_trade.avg_orders_filled-1]

                    average_entry_price = weighted_average_price(
                        entry_price=current_trade.entry_price,
                        base_quantity=current_trade.base_quantity,
                        avg_prices=filled_prices,
                        avg_quantities=filled_quantities
                    )
                    current_tp_price = average_entry_price * (1 + (bot_config.take_profit/100))
                    current_trade.avg_orders_filled += 1

            elif not in_trade:
                current_trade = open_trade(asset, row, bot_config)
                current_tp_price = current_trade.entry_price * (1 + (bot_config.take_profit/100))
                in_trade = True

    print(len(trades))

        
    # pull data at the lowest timeframe (since it's DCA)
    # iterate through df for each pair in bot config


