# -------------------------------------------------------------------------------------------------
# Broker Module
# -------------------------------------------------------------------------------------------------
# Author: Maxime Sirois
# -------------------------------------------------------------------------------------------------
"""
Module used to pass transactions.
"""
# -------------------------------------------------------------------------------------------------

from . import api


class OperationError(Exception):
    pass


class Broker:
    def __init__(self, config, db):
        self._config = config
        self._db = db
        self.client = api.AlphaVantageClient(**dict(self._config.items('API')))

    def get_number_of_shares(self, symbol):
        return self._db.get_number_of_shares(symbol)

    def buy(self, symbol, quantity):
        """Buy a given number of a shares.

        Args:
            symbol (str): The Security's ticker.
            quantity (int): The number of shares to buy.

        Returns:
            None
        """
        data = self.client.get_global_quote(symbol)
        price = data['price']
        self._db.buy(symbol, price, quantity)

    def sell(self, symbol, quantity):
        """Sell a given number of a shares.

        Args:
            symbol (str): The Security's ticker.
            quantity (int): The number of shares to buy.

        Returns:
            None
        """
        owned_shares = self.get_number_of_shares(symbol)

        if owned_shares < quantity:
            raise OperationError(f'Number of shares owned ({owned_shares}) is lower than the '
                                 f'quantity of shares to sell ({quantity}).')
        data = self.client.get_global_quote(symbol)
        price = data['price']
        self._db.sell(symbol, price, quantity)

    def calculate_profit(self, symbol):
        """Calculate the profit of a given symbol"""
        return self._db.get_profit(symbol)
