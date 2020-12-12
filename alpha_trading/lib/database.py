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


class Database:

    _INSERT_TEMPLATE = "INSERT INTO $table ($fields) VALUES ($values);"

    def __init__(self, **kwargs):
        db_path = Path(kwargs.get('database')).resolve()
        self.connection = sqlite3.connect(db_path)
        self.connection.isolation_level = None

    def execute(self, statement):
        cursor = self.connection.cursor()
        cursor.execute(statement)
        if 'SELECT' in statement.upper():
            return cursor.fetchall(), [e[0] for e in cursor.description]
        else:
            self.connection.commit()

    @staticmethod
    def _build_insert(table, payload):
        """
        Insert a Single line into the database by providing a dictionary having key (field name)
        and values.

        Args:
            table (str): The name of the table in which to insert.
            payload (dict): Example:
                {
                    "1. From_Currency Code": "USD",
                    "2. From_Currency Name": "United States Dollar",
                    "3. To_Currency Code": "JPY",
                    "4. To_Currency Name": "Japanese Yen",
                    "5. Exchange Rate": "107.41400000",
                    "6. Last Refreshed": "2020-04-15 19:14:35",
                    "7. Time Zone": "UTC",
                    "8. Bid Price": "107.41200000",
                    "9. Ask Price": "107.41600000"
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
