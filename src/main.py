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
    # bot_config = BotConfig(
    #     base_order_size=20,
    #     averaging_order_size=40,
    #     max_averaging_orders=6,
    #     averaging_order_size_multiplier=1.28,
    #     price_deviation=1.5,
    #     averaging_order_step_multiplier=1.85,
    #     take_profit=1.5,
    #     reinvest_profit=100,
    #     pairs=[Asset.ADA_USD],
    #     timeframes=[Timeframe.H1]
    # )

    # backtest_config = BacktestConfig(
    #     start_date=datetime(2021,1,1,0,0,0),
    #     end_date=datetime.now()
    # )

    # backtest.run_dca_backtest(
    #     backtest_config=backtest_config, 
    #     bot_config=bot_config
    #     )

    df = coindesk_api.get_OHLC(
        from_date=datetime(2025,1,1),
        to_date=datetime.now(),
        pair=Asset.ADA_USD,
        timeframe=Timeframe.H1)

    # df = get_OHLC(pair = "ADAUSD", from_date = "01-01-2020")
    # df = data.get_df("ADAUSD", Timeframe.H1, file_type='PARQUET')
    # print(df)
    # print(get_account_balance())

    # from_date = datetime(2021, 1, 1, 0, 0, 0)
    # coindesk_api.get_OHLC(from_date=from_date)
    


if __name__ == "__main__":
    main()