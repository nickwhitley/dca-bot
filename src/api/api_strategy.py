from constants import Asset
from constants import Timeframe
from datetime import datetime
from pandas import DataFrame

class APIStrategy:
    def __init__(self, api):
        self.api = api

    def get_OHLC(self, pair: Asset, timeframe: Timeframe, from_date: datetime, to_date: datetime):
        return self.api.get_OHLC(pair, timeframe, from_date, to_date)