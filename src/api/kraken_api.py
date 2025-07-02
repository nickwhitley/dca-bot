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

BASE_URL = 'https://api.kraken.com'

available_timeframes = {
    "1M": 1,
    "5M": 5,
    "15M": 15,
    "30M": 30,
    "1H": 60,
    "4H": 240,
    "1D": 1440,
    "1W": 10080,
    "15D": 21600
}


def make_request(path, params=None, data=None, headers=None, verb='get', code=200):
    full_url = f"{ BASE_URL }/{ path }"
    # print(f"full_url: { full_url }")
    # print(f"params: { params }")
    # print(f"data: { data }")
    # print(f"headers: { headers }")

    try:
        response = None
        if verb == 'get':
            response = requests.get(full_url, params=params, data=data, headers=headers)
        if verb == 'post':
            response = requests.post(full_url, params=params, data=data, headers=headers)
        if response == None:
            raise Exception('response was none.')
        if response.status_code == code:
            return True, response.json()
        else:
            return False, response.json()
    except Exception as ex:
        return False, {'Exception': ex }


def get_OHLC(pair=None, timeframe="1H", from_date=""):

    if timeframe not in available_timeframes.keys():
        print(f"timeframe: { timeframe } is invalid. Available timeframe: { available_timeframes.keys() }")
        return

    path = "/0/public/OHLC"
    since = time.mktime(datetime.datetime.strptime(from_date, "%m-%d-%Y").timetuple())

    params = {
        "pair": pair,
        "interval": available_timeframes[timeframe],
        "since": since
    }

    ok, response_data = make_request(
        path = path, 
        params = params
    )
    
    if ok and response_data["error"] == []:
        df = pd.DataFrame(response_data["result"][pair], columns=['timestamp', 'open', 'high', 'low', 'close', 'vwap', 'volume', 'count'])
        df['timestamp'] = df['timestamp'].apply(lambda x: strftime('%m-%d-%Y %H:%M', localtime(x)))
        df_name = f"{ pair }-{ timeframe }-{ from_date.replace('/', '.') }"
        data.save_df_to_pkl(df, df_name)
        return df
    else:
        print(f"Kraken api error: response_data["error"]")


def get_account_balance():
    path = "/0/private/Balance"

    data = {}
    nonce = get_nonce()
    data["nonce"] = nonce

    headers = {}
    headers["Content-Type"] = "Application/json"
    headers["API-Key"] = API_KEY
    headers["API-Sign"] = get_signature(PRIVATE_KEY, json.dumps(data), nonce, path)

    ok, response_data = make_request(
        path = path,
        data = json.dumps(data).encode(),
        headers = headers,
        verb = 'post'
    )

    print(response_data)

