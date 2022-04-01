# https://finance.yahoo.com/
import os
from datetime import datetime
from time import sleep
import locale


import yfinance as yf
from rich import print as rprint


def get_date_time(fmt: str = '%d/%m/%Y %H:%M:%S') -> datetime:
    return datetime.now().strftime(format=fmt)


def to_currency(price: str, currency: str, international: bool = False) -> str:
    locate = {
        'USD': 'en_US.UTF-8',
        'BRL': 'pt_BR.UTF-8',
        'GBP': 'en_GB.UTF-8',
        'EUR': 'en_IE.UTF-8',
    }

    locale.setlocale(locale.LC_ALL, locate[currency])

    return locale.currency(price, grouping=True, international=international)


time_to_reload = 30
tickers = ('BTC-USD', 'HASH11.SA', 'DEVA11.SA')
tickers_text = ' '.join(tickers)


for index in range(100):
    if index % 3 == 0:
        os.system('clear')

    data = yf.Tickers(tickers_text)
    rprint(get_date_time())

    for ticker in data.tickers.items():
        price = to_currency(
            ticker[1].info['regularMarketPrice'],
            ticker[1].info['currency']
        )
        shortName = ticker[1].info['shortName']
        rprint(f'{ticker[0]}: {price} - {shortName}')

    rprint()

    sleep(time_to_reload)
