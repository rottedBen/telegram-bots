from binance.client import Client
from pprint import pprint
import os

import datetime

clef = os.environ.get('BINANCE_API_KEY')
secret = os.environ.get('BINANCE_API_SECRET')

client = Client(clef, secret)

t_from = 1604660400000
to = 1604745000000

# candles = client.get_klines(symbol='BTCUSDT', interval="5m", startTime=t_from, endTime=to)

# pprint(candles)

import pandas as pd


def datteeesss(t_from, t_to):
    time_diff = round((t_to - t_from) / (1000 * 60))
    frequency = str(5) + 'min'

    time_start = datetime.datetime.fromtimestamp(round(t_from / 1000) + 1)
    time_end = datetime.datetime.fromtimestamp(round(t_to / 1000) + 1)

    pprint(time_start)
    pprint(time_end)
    pprint(frequency)

    date_list = pd.date_range(start=time_start, end=time_end, freq=frequency).to_pydatetime().tolist()
    pprint(date_list)


if __name__ == '__main__':
    datteeesss(t_from, to)