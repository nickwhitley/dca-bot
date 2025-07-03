import os
import sys
from api.kraken_api import get_OHLC
from api.kraken_api import get_account_balance
from data import data
from data.data import Timeframe
from loguru import logger

@logger.catch
def main():
    # get_OHLC(pair = "ADAUSaasdfD", from_date = "06-15-2025")
    # df = data.get_df_from_pkl("ADAUSD", Timeframe.H1)
    # print(df)
    get_account_balance()


if __name__ == "__main__":
    main()