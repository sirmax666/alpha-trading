# -------------------------------------------------------------------------------------------------
# Database Module
# -------------------------------------------------------------------------------------------------
# Author: Maxime Sirois
# -------------------------------------------------------------------------------------------------
"""
Database interfaces.
"""
# -------------------------------------------------------------------------------------------------

import re
from pathlib import Path
import sqlite3
from string import Template

from .constants import TRANSACTION_FEE


class RowsNotFoundError(Exception):
    pass


class Database:

    _INSERT_TEMPLATE = "INSERT INTO $table ($fields) VALUES ($values);"
    _TRANSACTION_TEMPLATE = ("INSERT INTO TRANSACTIONS (SYMBOL, TYPE, PRICE, QUANTITY) "
                             "VALUES (?, ?, ?, ?);")

    def __init__(self, **kwargs):
        db_path = Path(kwargs.get('database')).resolve()
        self.connection = sqlite3.connect(db_path)
        self.connection.isolation_level = None

    def execute(self, statement, args=None):
        cursor = self.connection.cursor()
        if args:
            cursor.execute(statement, args)
        else:
            cursor.execute(statement)
        if 'SELECT' in statement.upper():
            return cursor.fetchall(), [e[0] for e in cursor.description]
        else:
            self.connection.commit()

    def buy(self, symbol, price, quantity):
        """Insert buy information into the database."""
        self.execute(self._TRANSACTION_TEMPLATE, args=(symbol, 'BUY', price, quantity))

    def sell(self, symbol, price, quantity):
        """Insert buy information into the database."""
        self.execute(self._TRANSACTION_TEMPLATE, args=(symbol, 'SELL', price, quantity))

    def get_number_of_shares(self, symbol):
        """Get the number of currently owned shares of a given ticker."""
        return self.bought_shares(symbol) - self.sold_shares(symbol)

    def bought_shares(self, symbol):
        return self._share_count(symbol, 'BUY')

    def sold_shares(self, symbol):
        return self._share_count(symbol, 'SELL')

    def get_profit(self, symbol):
        return self._share_price(symbol, 'BUY') - self._share_price(symbol, 'SELL')

    def _share_count(self, symbol, action='BUY'):
        q = "SELECT SUM(QUANTITY) FROM TRANSACTIONS WHERE SYMBOL=? AND TYPE=?;"
        result, hdr = self.execute(q, args=(symbol, action))
        if not result[0]:
            raise RowsNotFoundError

        return result[0][0] or 0

    def _share_price(self, symbol, action):
        q = """SELECT
            SUM(PRICE * QUANTITY - ?)
            FROM TRANSACTIONS
            WHERE SYMBOL=? AND TYPE=?;"""
        result, hdr = self.execute(q, args=(TRANSACTION_FEE, symbol, action))
        if not result[0]:
            raise RowsNotFoundError

        return result[0][0] or 0

    @staticmethod
    def _build_insert(table, payload):
        """
        Insert a Single line into the database by providing a dictionary having key (field name)
        and values.

        Args:
            table (str): The name of the table in which to insert.
            payload (dict): Example:
                {
                    "01. symbol": "IBM",
                    "02. open": "124.0800",
                    "03. high": "125.5100",
                    "04. low": "123.6100",
                    "05. price": "124.2700",
                    "06. volume": "4481416",
                    "07. latest trading day": "2020-12-11",
                    "08. previous close": "124.9600",
                    "09. change": "-0.6900",
                    "10. change percent": "-0.5522%"
                }

        Returns:
            None
        """
        field_names = []
        values = []
        for field, value in payload.items():
            field_names.append(standardise(field))
            values.append(enquote(value))

        fields_str = ", ".join(field_names)
        values_str = ", ".join(values)
        t = Template(Database._INSERT_TEMPLATE)
        return t.substitute(table=table, fields=fields_str, values=values_str)


def standardise(s):
    return re.sub(r"^[0-9]+", "", s).strip(". ").replace(" ", "_").upper()


def enquote(s):
    """
    Enquote string if it's not numeric.

    Args:
        s (str): The string to enquote.

    Returns:
        str: A quoted string or unquoted numeric value as a string.
    """
    try:
        float(s)
    except ValueError:
        s_ = f'"{s}"'
    else:
        s_ = s
    return s_
