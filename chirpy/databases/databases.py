from typing import Callable, Dict, Tuple, Union

# maps names to lookup functions
DATABASES: Dict[Tuple[Union["lookup", "exists"], str], Callable] = {}

import logging

logger = logging.getLogger("chirpylogger")


def database_lookup(database_name):
    def inner(func):
        DATABASES[("lookup", database_name)] = func
        logger.warning(f"Installing {database_name}")
        return func

    return inner


def database_exists(database_name):
    def inner(func):
        DATABASES[("exists", database_name)] = func
        logger.warning(f"Installing {database_name}")
        return func

    return inner


def lookup(database_name, *args):
    logger.debug(f"Looking for {args} in {database_name}.")
    return DATABASES[("lookup", database_name)](*args)


def exists(database_name, *args):
    logger.debug(f"Looking for {args} in {database_name}.")
    return DATABASES[("exists", database_name)](*args)
