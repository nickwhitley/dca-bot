from constants import Asset
from bot.bot_config import BotConfig
from backtesting.backtest_config import BacktestConfig
from datetime import datetime
from data import data

def run_dca_backtest(backtest_config: BacktestConfig, bot_config: BotConfig):
    for pair in bot_config.pairs:
        for timeframe in bot_config.timeframes:
            df = data.get_df(
                pair=pair,
                timeframe=timeframe
            )
            print(df)
    # pull data at the lowest timeframe (since it's DCA)
    # iterate through df for each pair in bot config


