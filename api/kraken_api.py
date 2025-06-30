import requests
import time
import datetime
from security.nonce import get_nonce
import json

BASE_URL = 'https://api.kraken.com/0'


def make_request(path, params=None, data=None, headers=None, verb='get', code=200):
    full_url = f"{ BASE_URL }/{ path }"

    try:
        response = None
        if verb == 'get':
            response = requests.get(full_url, params=params, data=data, headers=headers)
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
    from_data is in format mm/dd/yyyy
    '''
    path="/public/OHLC"
    since = time.mktime(datetime.datetime.strptime(from_date, "%d/%m/%Y").timetuple())

    for pair in pairs:
        params = {
            "pair": pair,
            "interval": str(timeframe),
            "since": since
        }

        ok, data = make_request(
            path = path, 
            params = params
        )
        
        if ok:
            return data
