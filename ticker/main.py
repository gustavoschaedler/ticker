# https://finance.yahoo.com/
import os
from datetime import datetime
from time import sleep

import yfinance as yf
from rich import print as rprint


def get_date_time(fmt: str = '%d/%m/%Y %H:%M:%S') -> datetime:
    return datetime.now().strftime(format=fmt)


tickers = ('BTC-USD', 'HASH11.SA', 'DEVA11.SA')

tickers_text = ' '.join(tickers)

for index in range(100):
    if index % 3 == 0:
        os.system('clear')

    data = yf.Tickers(tickers_text)
    rprint(get_date_time())

    for ticker in data.tickers.items():
        rprint(f'{ticker[0]}: {ticker[1].info["regularMarketPrice"]}')

    rprint()

    sleep(30)
