from backtesting.backtest_result import BacktestResult
from constants import Asset
from bot.bot_config import BotConfig
from backtesting.backtest_config import BacktestConfig

from datetime import datetime
from data import data

def run_dca_backtest(backtest_config: BacktestConfig, bot_config: BotConfig) -> BacktestResult:
    for asset in bot_config.assets:
        df = data.get_df(asset=asset)
        print(df)
    # pull data at the lowest timeframe (since it's DCA)
    # iterate through df for each pair in bot config


