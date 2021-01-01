# -------------------------------------------------------------------------------------------------
# Environment Module
# -------------------------------------------------------------------------------------------------
# Author: Maxime Sirois
# -------------------------------------------------------------------------------------------------
"""
Responsible for generating the environment.
"""
# -------------------------------------------------------------------------------------------------


import logging
from pathlib import Path
import sqlparse

from . import database
from .broker import Broker


logger = logging.getLogger(__name__)


class Environment:
    """Enrivonment Setup
    Contains the User as specified in the configs and also the api client object.
    """
    def __init__(self, config, **kwargs):
        self.config = config
        self.db = database.Database(database=config.get('DATABASE', 'DATABASE'))
        self.broker = Broker(config, self.db)
        self.initialize()
        self.user = User(self.db, self.config.get('GENERAL', 'USERNAME'))

    def initialize(self, teardown=False):
        """Initialize Environment."""
        logger.info("-------------- Initialization --------------")
        if teardown:
            logger.info("Tearing Down Environment")
            self.tear_down()

        logger.info("Initializing SQL Environment")
        self._setup_sql()

    def _setup_sql(self):
        sql_path = Path(self.config.get('ENVIRONMENT', 'SQL')).resolve()
        statements = read_sql(sql_path)
        for statement in statements:
            stmt = sqlparse.format(str(statement), strip_comments=True)
            stdout_stmt = stmt.strip().replace("\n", " ")[:50] + "..."
            logger.info(f"Running: {stdout_stmt}")
            self.db.execute(stmt)

    def tear_down(self):
        pass


class User:
    """User Class
    Most useful to link the user's wallet instance.
    """
    def __init__(self, db, username):
        self.db = db
        self.username = username
        self.info = self._set_info()
        self.user_id = self.info.get('USER_ID')
        self.first_name = self.info.get('FIRST_NAME')
        self.last_name = self.info.get('LAST_NAME')
        self.creation_tmsp = self.info.get('CREATION_TMSP')
        self.wallet = Wallet(self.db, self.user_id)

    def _set_info(self):
        stmt = ("SELECT * "
                "FROM USER_INFO "
                f"WHERE USER_NAME='{self.username}';")
        res, hdr = self.db.execute(stmt)
        return dict(zip(hdr, res[0]))


class Wallet:
    def __init__(self, db, user_id):
        self.db = db
        self.user_id = user_id
        self.balance = self._init_balance()

    def _init_balance(self):
        stmt = ("SELECT SUM(DEPOSIT) - SUM(WITHDRAWAL) "
                "FROM USER_DEPOSITS "
                f"WHERE USER_ID={self.user_id};")
        res, hdr = self.db.execute(stmt)
        if not res:
            account_balance = 0
        else:
            account_balance = res[0][0]
        return account_balance


def read_sql(path):
    """
    Read a SQL file with queries.

    Args:
        path (str): Absolute file path.

    Returns:
        tuple: tuple of sql statements.
    """
    with open(path, 'r') as f_in:
        content = f_in.read()
    return sqlparse.parse(content)
