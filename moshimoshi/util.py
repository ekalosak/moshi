""" Various helper utilities. """

from functools import wraps
from time import time
from typing import Callable

from loguru import logger

logger.success("loaded")


def timed(f: Callable):
    """Log timing of a function."""

    @wraps(f)
    def timer(*a, **k):
        t0 = time()
        logger.trace(f"START {f.__name__}")
        res = f(*a, **k)
        td = time() - t0
        logger.trace("END   {}\t{:10.4f} sec".format(f.__name__, td))
        return res

    return timer
