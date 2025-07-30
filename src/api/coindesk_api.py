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
from loguru import logger
from security.coindesk_key import API_KEY

BASE_URL = 'https://data-api.coindesk.com'
DATA_LIMIT = 2000

def make_request(
        path: str,
        params: dict[str, Any],
        headers: dict[str, Any],
        verb: Literal['GET', 'POST'] = 'GET',
        retry_on: list[int] = [429, 502, 503, 504],
        retry_delay: float = 2.0,
        retry_max: int = 3
) -> Any:
    url = f"{BASE_URL}{path}"
    retries = 0
    logger.info(f"calling {url} with params: {params}")
    while retries < retry_max:
        try:
            response = requests.request(
                method=verb,
                url=url,
                params=params,
                headers=headers
            )
        except (requests.ConnectionError, requests.ConnectTimeout):
            retries += 1
            logger.warning(f"retrying call to {url}, retries: {retries}")
            time.sleep(retry_delay)
            continue
        if response.status_code in retry_on:
            retries += 1
            logger.warning(f"retrying call to {url} due to status code: {response.status_code}, retries: {retries}")
            time.sleep(retry_delay * retries)
            continue
        elif response.status_code not in range(200, 299):
            raise ApiError(
                f"Call to {url} yeilded a {response.status_code}"
                f'response with: {response.content}'
            )
        elif response is None:
            logger.error(f"call to {url} yielded {response.status_code}, response is None.")
            return None
        else:
            logger.info(f"call to {url} is returning response.")
            return response.json()



def get_OHLC(
        from_date: datetime,
        to_date: datetime = datetime.now().replace(minute=0,second=0,microsecond=0),
        asset: Asset = Asset.ADA_USD,
        timeframe: Timeframe = Timeframe.M1,
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
        chunk_end = min(current_date + timedelta(minutes=DATA_LIMIT), to_date)
        print(f"Current chunk end {chunk_end}")
        chunk_end_timestamp = chunk_end.timestamp()
        total_data_ticks = (chunk_end - current_date).total_seconds() / 60 / timeframe.value
        instrument = asset.value.replace('_', '-')
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
        headers = {
            "Authorization": f"ApiKey {API_KEY}"
        }

        logger.info(f"making OHLC request")
        chunk_result = make_request(
            path=path,
            params=params,
            headers=headers
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
    
    df['timestamp'] = pd.to_datetime(df['timestamp'], unit='s')

    df_name = f"{ asset.value.replace('/', '_') }-{ timeframe.name }-{ from_date.strftime('%m-%d-%Y') }"
    try:
        data.save_df(
            df=df,
            file_name=df_name
        )
    except:
        print("failed to save")
    finally:
        return df


    