from typing import Callable, Dict, Tuple, Union

# maps names to lookup functions
DATABASES : Dict[Tuple[Union["lookup", "exists"], str], Callable] = {}

import logging

logger = logging.getLogger('chirpylogger')

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
	return DATABASES[("lookup", database_name)](*args)

def exists(database_name, database_key):
	# having variable number of args here seems like more trouble than it is worth
	return DATABASES[("exists", database_name)](database_key)

