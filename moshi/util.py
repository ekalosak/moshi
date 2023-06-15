import asyncio
import functools
from http.cookies import SimpleCookie
import sys
import uuid

import pyfiglet
from loguru import logger
from loguru._defaults import LOGURU_FORMAT

def _setup_loguru():
    LOG_FORMAT = LOGURU_FORMAT + " | <g><d>{extra}</d></g>"
    logger.remove()
    logger.add(sink=sys.stderr, format=LOG_FORMAT, colorize=True)
    logger.add("logs/server.log", rotation="10 MB")
    logger.level("INSTRUCTION", no=38, color="<light-yellow><bold>")
    logger.level("SPLASH", no=39, color="<light-magenta><bold>")

def async_with_pcid(f):
    """Decorator for contextualizing the logger with a PeerConnection uid."""

    @functools.wraps(f)
    async def wrapped(*a, **k):
        pcid = uuid.uuid4()
        with logger.contextualize(PeerConnection=str(pcid)):
            return await f(*a, **k)

    return wrapped


def aio_exception_handler(loop: "EventLoop", context: dict[str, ...]):
    logger.error(context)


def splash(text: str):
    logger.log(
        "SPLASH",
        "\n" + pyfiglet.Figlet(font="roman").renderText(text),
    )

def remove_non_session_cookies(req: 'aiohttp.web_request.Request', session_name: str) -> 'aiohttp.web_request.Request':
    """Because Python's http.cookie.SimpleCookie parsing craps out when it hits an invalid component, see
    notes/issues/http-headers for the whole saga, this function removes all but the session cookie from a request."""
    in_cookie_string = req.headers.get('Cookie')
    if in_cookie_string is None:
        return req
    session_cookie = None
    for chunk in in_cookie_string.split(';'):
        ck = SimpleCookie(chunk)
        assert len(ck) in (0, 1)
        if session_name in ck.keys():
            session_cookie = ck
            logger.debug(f"Found session cookie: {session_cookie}")
            break
    if session_cookie is None:
        cookie_str = ""
    else:
        cookie_str = session_cookie.output().split('Set-Cookie: ')[1]
    logger.debug(f"Extracted session cookie string: {cookie_str}")
    hdr = req.headers.copy()
    hdr['Cookie'] = cookie_str
    out = req.clone(headers=hdr)
    return out
