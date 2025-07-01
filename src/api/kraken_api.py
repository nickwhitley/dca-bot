import requests
import time
import datetime
from security.nonce import get_nonce
from security.nonce import get_signature
from security.SEC_KEY import API_KEY, PRIVATE_KEY
import json
import pandas as pd

BASE_URL = 'https://api.kraken.com'


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


def get_OHLC(pairs=None, timeframe=60, from_date=""):
    '''
    timeframe is in minutes
    timeframe possible values: [1, 5, 15, 30, 60, 240, 1440 (1 day), 10080 (1 week), 21600 (15 days)]
    from_date is in format mm/dd/yyyy
    '''
    path = "/0/public/OHLC"
    since = time.mktime(datetime.datetime.strptime(from_date, "%d/%m/%Y").timetuple())

    for pair in pairs:
        params = {
            "pair": pair,
            "interval": str(timeframe),
            "since": since
        }

        ok, response_data = make_request(
            path = path, 
            params = params
        )
        
        if ok:
            df = pd.DataFrame(response_data["result"][pair], columns=['timestamp', 'open', 'high', 'low', 'close', 'vwap', 'volume', 'count'])
            print(df)

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

