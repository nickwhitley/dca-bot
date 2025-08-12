import argparse
import os
import sys
from api import coindesk_api
from data import data
from data.data import Timeframe
from loguru import logger
from datetime import datetime
from bot.bot_config import BotConfig
from backtesting.backtest_config import BacktestConfig
from constants import Asset, Timeframe
from backtesting import backtest

@logger.catch
def main():
    parser = argparse.ArgumentParser(description="Run DCA Bot Backtest")
    parser.add_argument("asset", type=str, help="Trading pair, e.g. ADA_USD")
    parser.add_argument("starting_balance", type=float, help="Starting balance for backtest")
    args = parser.parse_args()

    try:
        asset_enum = Asset(args.asset.upper())
    except ValueError:
        raise ValueError(f"Invalid asset '{args.asset}'. Must be one of: {[a.value for a in Asset]}")

    bot_config = BotConfig(
        base_order_size=50,
        averaging_order_size=100,
        max_averaging_orders=6,
        averaging_order_size_multiplier=1.28,
        price_deviation=1.5,
        averaging_order_step_multiplier=1.85,
        take_profit=1.5,
        reinvest_profit_pct=0,
        assets=[asset_enum],
        timeframes=[Timeframe.H1]
    )

    bot_config.scale_to_starting_balance(args.starting_balance)

    backtest_config = BacktestConfig(
        start_date=datetime(2023,1,1,0,0,0),
        end_date=datetime.now(),
        starting_balance=args.starting_balance
    )

    result = backtest.run_dca_backtest(
        backtest_config=backtest_config, 
        bot_config=bot_config
        )
    
    print(bot_config)
    print(backtest_config)
    print(result)


if __name__ == "__main__":
    main()