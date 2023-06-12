import asyncio
import functools
import sys
import uuid

from loguru import logger
from loguru._defaults import LOGURU_FORMAT
import requests

def setup_loguru():
    LOG_FORMAT = LOGURU_FORMAT + " | <g><d>{extra}</d></g>"
    logger.remove()
    logger.add(sink=sys.stderr, format=LOG_FORMAT, colorize=True)
    logger.add("logs/server.log", rotation="10 MB")

def async_with_pcid(f):
    """ Decorator for contextualizing the logger with a PeerConnection uid. """
    @functools.wraps(f)
    async def wrapped(*a, **k):
        pcid = uuid.uuid4()
        with logger.contextualize(PeerConnection=str(pcid)):
            return await f(*a, **k)
    return wrapped

def aio_exception_handler(loop: 'EventLoop', context: dict[str, ...]):
    logger.error(context)
