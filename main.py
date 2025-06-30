import os
import sys
from api.kraken_api import get_OHLC


def main():
    get_OHLC(pairs = ["ADAUSD"], from_date = "01/01/2025")
#pseudo code
#live trading:
#check if in trade
    #if not:
        #enter trade
    #if in trade:
        #check to see if price is at next averaging target


if __name__ == "__main__":
    main()