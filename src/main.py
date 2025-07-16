import os
import sys
from api.kraken_api import get_OHLC
from api.kraken_api import get_account_balance
from api import coindesk_api
from data import data
from data.data import Timeframe
from loguru import logger
from datetime import datetime

@logger.catch
def main():
    # df = get_OHLC(pair = "ADAUSD", from_date = "01-01-2020")
    # df = data.get_df("ADAUSD", Timeframe.H1, file_type='PARQUET')
    # print(df)
    # print(get_account_balance())

    from_date = datetime(2021, 1, 1, 0, 0, 0)
    coindesk_api.get_OHLC(from_date=from_date)
    


if __name__ == "__main__":
    main()