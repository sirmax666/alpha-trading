# -------------------------------------------------------------------------------------------------
# Alpha Trading
# -------------------------------------------------------------------------------------------------
"""
Trading Program based on the alphavantage API.
Just for fun.
"""
# -------------------------------------------------------------------------------------------------

import argparse
from datetime import datetime
import logging
from pathlib import Path
import os

from lib.constants import get_config
from lib.environment import Environment

HERE = Path(os.path.realpath(__file__)).parent.resolve()
LOG_FOLDER = HERE.parent / 'logs'


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('-v', '--verbose', action='store_true', help='Increase Verbosity')
    return parser.parse_args()


def set_log(file_path: str, debug: bool) -> None:
    """Set the logs.

    Args:
        file_path (str): Absolute log file path.
        debug (bool): Set to debug level.

    Returns:
        None
    """
    logging.basicConfig(filename=file_path,
                        filemode='w+',
                        format='[%(asctime)s] %(levelname)-8s: %(message)s',
                        datefmt="%Y-%m-%d %H:%M:%S",
                        level=logging.DEBUG if debug else logging.INFO)

    console = logging.StreamHandler()
    console.setLevel(logging.INFO)
    formatter = logging.Formatter('%(levelname)-8s: %(message)s')
    # tell the handler to use this format
    console.setFormatter(formatter)
    # add the handler to the root logger
    logging.getLogger('').addHandler(console)


def main():
    """
    Main Program
    """
    args = parse_args()
    config = get_config(credentials=True)

    tmsp = datetime.now().strftime("%Y%m%d%H%M%S")

    log_path = LOG_FOLDER / f'alpha-{tmsp}.log'
    set_log(log_path, debug=args.verbose)

    env = Environment(config)

    logging.info(env.user.first_name)

    # logging.info('Buy 100 netflix')
    # env.broker.buy(symbol='NFLX', quantity=100)
    # logging.info('Sell 50 netflix')
    # env.broker.sell(symbol='NFLX', quantity=50)
    logging.info('Netflix Profit:')
    logging.info(env.broker.calculate_profit('NFLX'))



if __name__ == '__main__':
    main()
