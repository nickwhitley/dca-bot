from constants import Asset
from constants import Timeframe
from datetime import datetime
from datetime import timedelta
import pandas as pd
from typing import Any, Literal
import requests
import time
from api.api_error import ApiError
from time import strftime, localtime
from data import data

BASE_URL = 'https://data-api.coindesk.com'
DATA_LIMIT = 2000

def make_request(
        path: str,
        params: dict[str, Any],
        verb: Literal['GET', 'POST'] = 'GET',
        retry_on: list[int] = [429, 502, 503, 504],
        retry_delay: float = 1.0,
        retry_max: int = 3
) -> Any:
    url = f"{BASE_URL}{path}"
    retries = 0
    while retries < retry_max:
        try:
            response = requests.request(
                method=verb,
                url=url,
                params=params
            )
        except (requests.ConnectionError, requests.ConnectTimeout):
            retries += 1
            time.sleep(retry_delay)
            continue
        if response.status_code in retry_on:
            retries += 1
            time.sleep(retry_delay)
            continue
        elif response.status_code not in range(200, 299):
            raise ApiError(
                f"Call to {url} yeilded a {response.status_code}"
                f'response with: {response.content}'
            )
        else:
            return response.json()



def get_OHLC(
        from_date: datetime,
        to_date: datetime = datetime.now().replace(minute=0,second=0,microsecond=0),
        pair: Asset = Asset.ADA_USD,
        timeframe: Timeframe = Timeframe.H1,
) -> pd.DataFrame|None:
    path = "/index/cc/v1/historical/"
    match timeframe:
        case Timeframe.D:
            path += "days"
        case Timeframe.H1:
            path += "hours"
        case Timeframe.M1:
            path += "minutes"
        case _:
            path += ""

    result = []
    print(f"Pulling data from {from_date} to {to_date}")
    current_date = from_date

    while current_date < to_date:
        chunk_end = min(current_date + timedelta(hours=2000), to_date)
        print(f"Current chunk end {chunk_end}")
        chunk_end_timestamp = chunk_end.timestamp()
        total_data_ticks = (chunk_end - current_date).total_seconds() / 60 / timeframe.value
        instrument = pair.value.replace('/', '-')

        params = {
            "groups": "OHLC",
            "to_ts": chunk_end_timestamp,
            "instrument": instrument,
            "limit": int(total_data_ticks),
            "market": "cadli",
            "aggregate": "1",
            "apply_mapping": "true",
            "response_format": "JSON",
            "fill": "true"
        }

        chunk_result = make_request(
            path=path,
            params=params
        )
        
        result += chunk_result['Data']

        current_date = chunk_end

    df = pd.DataFrame(result)
    df = df.rename(columns={
        'UNIT': 'timeframe', 
        'TIMESTAMP': 'timestamp', 
        'OPEN': 'open', 
        'HIGH': 'high', 
        'LOW': 'low', 
        'CLOSE': 'close'
        }, errors='raise').drop(['timeframe'], axis=1)
    
    df['timestamp'] = df['timestamp'].apply(lambda x: strftime('%m-%d-%Y %H:%M', localtime(x)))
    print(df.head(20))
    print(df.tail(20))

    df_name = f"{ pair.value.replace('/', '_') }-{ timeframe.name }-{ from_date.strftime('%m-%d-%Y') }"
    data.save_df(df, df_name, 'PARQUET')


    