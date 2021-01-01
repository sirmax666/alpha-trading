# -------------------------------------------------------------------------------------------------
# api
# -------------------------------------------------------------------------------------------------
# Author: Maxime Sirois
# -------------------------------------------------------------------------------------------------
"""
The API Class that is used to get quotes.
"""
# -------------------------------------------------------------------------------------------------


import logging
import re
import requests

logger = logging.getLogger(__name__)


class ApiQueryError(Exception):
    pass


class API:

    """Parent API class"""
    def __init__(self, url, api_key):
        self.url = url
        self.api_key = api_key

    def _get(self, payload):
        payload.update({'apikey': self.api_key})
        logger.debug(payload)
        return requests.get(self.url, params=payload)


class AlphaVantageClient(API):

    def get_rate(self, from_currency, to_currency):
        payload = {
            "function": "CURRENCY_EXCHANGE_RATE",
            "from_currency": from_currency,
            "to_currency": to_currency
        }
        data = self._get(payload)
        d_data = data.json().get("Realtime Currency Exchange Rate")
        if not data:
            raise ApiQueryError

        d_data = standardize_keys(d_data)
        return d_data

    def get_global_quote(self, symbol):
        """Get the live quote."""
        payload = {
            "function": "GLOBAL_QUOTE",
            "symbol": symbol
        }
        response = self._get(payload)
        data = response.json().get("Global Quote")
        if not data:
            raise ApiQueryError
        s_data = standardize_keys(data)
        logger.info(s_data)
        return s_data


def standardize_keys(d):
    std_keys = [standardize(k) for k in d.keys()]
    return dict(zip(std_keys, list(d.values())))


def standardize(s):
    return re.sub(r"^[0-9]+", "", s).strip(". ").replace(" ", "_").lower()
