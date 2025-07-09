import requests
import time
import datetime
from security.nonce import get_nonce
from security.nonce import get_signature
from security.SEC_KEY import API_KEY, PRIVATE_KEY
import json
import pandas as pd
from data import data
from time import strftime, localtime
from constants import Timeframe
from typing import Any, Literal

BASE_URL = 'https://api.kraken.com'

class ApiError(Exception):
    """
    Handles any Api Related Errors
    """

def make_request(
        path: str, 
        params: dict[str, Any] | None = None, 
        data: bytes | None = None, 
        headers: dict[str, str] | None = None, 
        verb: Literal['GET', 'POST', 'PUT', 'PATCH', 'DELETE'] = 'GET',
        use_nonce: bool = False,
        retry_on: list[int] | None = None,
        retry_delay: float = 1.0,
        retry_max: int = 3
) -> Any:
    
    if not retry_on:
        retry_on = [429, 502, 503, 504]

    url = f"{BASE_URL}/{path}"
    retries = 0

    while retries < retry_max:
        if use_nonce:
            nonce = get_nonce()

            payload = {}
            if data:
                payload = json.loads(data.decode())
            payload['nonce'] = nonce
            data = json.dumps(payload).encode()
            
            headers = headers or {}
            headers.setdefault('Content-Type', 'Application/json')
            headers['API-Key'] = API_KEY
            headers['API-Sign'] = get_signature(
                PRIVATE_KEY,
                data.decode(),
                nonce,
                path
            )

        try:
            response = requests.request(
                method=verb,
                url=url,
                params=params,
                data=data,
                headers=headers,
            )
        except (requests.ConnectionError, requests.ConnectTimeout):
            retries += 1
            time.sleep(retry_delay)
            continue
        
        if response.status_code in retry_on:
            retries += 1
            time.sleep(retry_delay)
        elif response.status_code not in range(200, 299):
            raise ApiError(
                f"Call to {url} yeilded a {response.status_code}"
                f'response with "{response.content}'
            )
        elif (error := response.json().get('error')) != []:
            raise ApiError(f'Api returned error: { error }')
        else:
            return response.json()
        
    raise ApiError(f'Max Retries exeeded to {url}')


def get_OHLC(
        pair: str="BTCUSD", 
        timeframe: Timeframe=Timeframe.H1, 
        from_date: str=""
) -> pd.DataFrame|None:
    
    path = "/0/public/OHLC"
    since = time.mktime(datetime.datetime.strptime(from_date, "%m-%d-%Y").timetuple())
    params = {
        "pair": pair,
        "interval": timeframe.value,
        "since": since
    }

    response = make_request(
        path = path, 
        params = params
    )
    
    df = pd.DataFrame(response["result"][pair], columns=['timestamp', 'open', 'high', 'low', 'close', 'vwap', 'volume', 'count']) 
    df['timestamp'] = df['timestamp'].apply(lambda x: strftime('%m-%d-%Y %H:%M', localtime(x)))

    df_name = f"{ pair }-{ timeframe.name }-{ from_date.replace('/', '.') }"
    data.save_df(df, df_name, 'PARQUET')

    return df


def get_account_balance() -> dict:
    path = "/0/private/Balance"

    response = make_request(
        path = path,
        verb = 'POST',
        use_nonce=True
    )
    
    return response['result']

