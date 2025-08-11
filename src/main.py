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

    bot_config = BotConfig(
        base_order_size=50,
        averaging_order_size=100,
        max_averaging_orders=6,
        averaging_order_size_multiplier=1.28,
        price_deviation=1.5,
        averaging_order_step_multiplier=1.85,
        take_profit=1.5,
        reinvest_profit_pct=0,
        assets=[Asset.ADA_USD],
        timeframes=[Timeframe.H1]
    )

    backtest_config = BacktestConfig(
        start_date=datetime(2023,1,1,0,0,0),
        end_date=datetime.now(),
        starting_balance=1_000
    )

    result = backtest.run_dca_backtest(
        backtest_config=backtest_config, 
        bot_config=bot_config
        )
    
    print(result)


if __name__ == "__main__":
    main()