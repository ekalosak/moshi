""" Various helper utilities. """

from functools import wraps
from time import time
from typing import Callable

from loguru import logger

logger.success("loaded")

def timed(f: Callable):
    """ Log timing of a function. """
    @wraps(f)
    def wrapper(*a, **k):
        t0 = time()
        logger.debug(f"START")
        res = f(*a, **k)
        td = time() - t0
        logger.debug(f"END\t{td} sec")
        return res
    return wrapper
