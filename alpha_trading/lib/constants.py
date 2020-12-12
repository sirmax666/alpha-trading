# -------------------------------------------------------------------------------------------------
# Constants
# -------------------------------------------------------------------------------------------------
# Author: Maxime Sirois
# -------------------------------------------------------------------------------------------------
"""
Globals
"""
# -------------------------------------------------------------------------------------------------


import configparser
import os
import re

# --- PATHS ---
_CURRENT_FOLDER = os.path.dirname(os.path.realpath(__file__))
MAIN_FOLDER = os.path.join(_CURRENT_FOLDER, '..')
PARAM_FOLDER = os.path.join(MAIN_FOLDER, 'param')
INI_PATH = os.path.join(PARAM_FOLDER, 'config.ini')
DB_PATH = os.path.join(PARAM_FOLDER, 'alpha.db')

# --- GLOBALS ---
NULL = ['NAN', 'NULL', 'N/A', 'NONE', '']


def get_config(ini_path=INI_PATH, credentials=False):
    """
    Get the configurations

    :return: config object
    """
    if not os.path.exists(ini_path):
        raise IOError(2, 'No such file', ini_path)
    config = configparser.ConfigParser()
    config._interpolation = configparser.ExtendedInterpolation()
    config.read(ini_path)
    if credentials:
        config = __map_credentials(config)
    return config


def __map_credentials(config):
    """Add credentials to the returned configparser object.

    The expected structure of the ini should be:
    --- config.ini ---
    [SECTION_NAME]
    VALUE_1 = a_value_not_mapped
    PASSWORD = {{REF_CREDS:MY-CREDS-SECTION:MY-CREDS-OPTION}}
    [CREDENTIALS]
    INI_PATH = /path/to/the/ini/credentials.ini

    --- credentials.ini ---
    [MY-CREDS-SECTION]
    MY-CREDS-OPTION = thisisafakepassword

    Args:
        config object: The configparser object.

    Returns:
        object: The modified configparser object with credentials.
    """
    CREDS_INI_FILE_PATH = config.get('CREDENTIALS', 'INI_PATH')
    config_creds = configparser.ConfigParser()
    config_creds._interpolation = configparser.ExtendedInterpolation()
    config_creds.read(CREDS_INI_FILE_PATH)
    # Go through sections and replace jinja styled strings
    for section in config.sections():
        dict_config = dict(config[section].items())
        for option, value in dict_config.items():
            match = re.search("{{([A-Z\\-:_]+)}}", value)
            if match:
                ref, sec, opt = match.group(1).split(":")
                config[section][option] = config_creds.get(sec, opt)
    return config
