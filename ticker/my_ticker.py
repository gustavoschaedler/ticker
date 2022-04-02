import locale


class Ticker:
    def __init__(self, name, short_name, currency, quantity, price):
        self.name = name
        self.short_name = short_name
        self.currency = currency
        self.quantity = quantity
        self.price = self.to_currency(price, currency)
        self.total = self.to_currency((quantity * price), currency)

    def to_currency(
        self, price: str, currency: str, international: bool = False
    ) -> str:
        locate = {
            'USD': 'en_US.UTF-8',
            'BRL': 'pt_BR.UTF-8',
            'GBP': 'en_GB.UTF-8',
            'EUR': 'en_IE.UTF-8',
        }

        locale.setlocale(locale.LC_ALL, locate[currency])

        return locale.currency(
            price, grouping=True, international=international
        )
