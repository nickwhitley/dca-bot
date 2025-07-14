import os
import sys
from api.kraken_api import get_OHLC
from api.kraken_api import get_account_balance
from data import data
from data.data import Timeframe
from loguru import logger

@logger.catch
def main():
    df = get_OHLC(pair = "ADAUSD", from_date = "01-01-2020")
    # df = data.get_df("ADAUSD", Timeframe.H1, file_type='PARQUET')
    print(df)
    # print(get_account_balance())


if __name__ == "__main__":
    main()