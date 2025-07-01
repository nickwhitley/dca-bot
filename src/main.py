import os
import sys
from api.kraken_api import get_OHLC
from api.kraken_api import get_account_balance


def main():
    get_OHLC(pair = "ADAUSD", from_date = "06-15-2025")
    # get_account_balance()


if __name__ == "__main__":
    main()