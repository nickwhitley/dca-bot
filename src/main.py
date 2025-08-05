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
    # df = data.get_df(asset=Asset.ADA_USD)
    # data.save_df(df, 'ADA_CSV',file_type='CSV')

    bot_config = BotConfig(
        base_order_size=20,
        averaging_order_size=40,
        max_averaging_orders=6,
        averaging_order_size_multiplier=1.28,
        price_deviation=1.5,
        averaging_order_step_multiplier=1.85,
        take_profit=1.5,
        reinvest_profit=0,
        assets=[Asset.ADA_USD],
        timeframes=[Timeframe.H1]
    )

    backtest_config = BacktestConfig(
        start_date=datetime(2023,1,1,0,0,0),
        end_date=datetime.now(),
        starting_balance=10_000
    )

    result = backtest.run_dca_backtest(
        backtest_config=backtest_config, 
        bot_config=bot_config
        )
    print(result.trades[0])
    print(result.trades[1])
    print(result.trades[2])
    print(result.trades[3])
    print(result.trades[4])
    print(result.trades[5])
    print(result.trades[6])
    print(result.trades[7])

    print(result.trades[8])

    print(result.trades[9])
    print(result.trades[75])
    print(len(result.trades))
    print(result.ending_balance)
    print(result.max_drawdown)
    print(result.average_drawdown)
    print(result.gain_loss)

    # TODO: Reinvest profit doesn't work, should increase balance and the base order size should rise respectively
    # TODO: Calculate max drawdown, avg trade lifetime, avg drawdown
    # TODO: Need to recalculate balances and order sizes to have accurate results, I can't do percentage tp off the starting balance of $10,000 when the actual bot usage is only around $500


if __name__ == "__main__":
    main()