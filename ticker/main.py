# https://finance.yahoo.com/
import os
import json
from datetime import datetime
from time import sleep
from pathlib import Path

import yfinance as yf
from rich import print as rprint

from ticker.my_ticker import Ticker


def get_date_time(fmt: str = '%d/%m/%Y %H:%M:%S') -> datetime:
    return datetime.now().strftime(format=fmt)


def get_data_tickers(tickers: str) -> yf.Tickers:
    return yf.Tickers(tickers)


time_to_reload = 30
file = Path('tickers.json')

if file.exists():
    file_data = file.read_text()

tickers = json.loads(file_data)

tickers_keys = [key[0] for key in tickers.items()]
tickers_text = ' '.join(tickers_keys)


for index in range(100):
    if index % 3 == 0:
        os.system('clear')

    data = get_data_tickers(tickers_text)
    rprint(get_date_time())

    for ticker in data.tickers.items():
        my_ticker = Ticker(
            ticker[0],
            ticker[1].info['shortName'],
            ticker[1].info['currency'],
            tickers[ticker[0]],
            ticker[1].info['regularMarketPrice'],
        )

        rprint(
            f'{my_ticker.name}: {my_ticker.price} x {my_ticker.quantity} = {my_ticker.total}'
        )

    rprint()

    sleep(time_to_reload)
