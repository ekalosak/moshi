from functools import wraps
from time import time

def call_count(f, ms=1000):
    """ Log the number of times the <f> gets called per <ms> milliseconds.
    This isn't threaded so it will only log when called, if appropriate.
    """
    f._call_count = 0
    f._t0 = time()

    @wraps(f)
    def wrapper(*a, **k):
        f._call_count += 1
        t1 = time()
        dt = (t1 - f._t0) * 1000.
        if dt > ms:
            logger.debug(f"{f.__name__} called {f._call_count} times in {dt} ms")
            f._t0 = t1
            f._call_count = 0
        return f(*a, **k)
    return wrapper
