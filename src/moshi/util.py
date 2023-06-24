import asyncio
import functools
from http.cookies import SimpleCookie
import os
import sys
from textwrap import shorten
import uuid

from google.cloud import logging
from google.protobuf.json_format import ParseError
from loguru import logger
from loguru._defaults import LOGURU_FORMAT
import pyfiglet

FILE_LOGS = int(os.getenv("MOSHILOGDISK", 0))
STDOUT_LOGS = int(os.getenv("MOSHILOGSTDOUT", 1))
CLOUD_LOGS = int(os.getenv("MOSHILOGCLOUD", 0))

def _gcp_log_severity_map(level: str) -> str:
    """Convert loguru custom levels to GCP allowed severity level.
    Source:
        - https://cloud.google.com/logging/docs/reference/v2/rest/v2/LogEntry#LogSeverity
    """
    match level:
        case "SUCCESS":
            return "INFO"
        case "INSTRUCTION":
            return "DEBUG"
        case "SPLASH":
            return None
        case _:
            return level

def _setup_loguru():
    # Loguru
    logger.level("INSTRUCTION", no=15, color="<light-yellow><bold>")
    logger.level("SPLASH", no=13, color="<light-magenta><bold>")
    LOG_FORMAT = LOGURU_FORMAT + " | <g><d>{extra}</d></g>"
    logger.remove()
    if STDOUT_LOGS:
        logger.add(sink=sys.stderr, format=LOG_FORMAT, colorize=True)
    if FILE_LOGS:
        logger.add("logs/server.log", rotation="10 MB")
    # Google logging  (https://github.com/Delgan/loguru/issues/789)
    if CLOUD_LOGS:
        logging_client = logging.Client()
        gcp_logger = logging_client.logger("gcp-logger")
        def log_to_gcp(message):
            severity = _gcp_log_severity_map(message.record["level"].name)
            if severity is not None:
                gcp_logger.log_text(message, severity=severity)
        logger.add(log_to_gcp)

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

# TODO needs testing obv v
def remove_non_session_cookies(req: 'aiohttp.web_request.Request', session_name: str) -> 'aiohttp.web_request.Request':
    """Because Python's http.cookie.SimpleCookie parsing craps out when it hits an invalid component, see
    notes/issues/http-headers for the whole saga, this function removes all but the session cookie from a request."""
    text_len = 64
    in_cookie_string = req.headers.get('Cookie')
    if in_cookie_string is None:
        return req
    session_cookie = None
    for chunk in in_cookie_string.split(';'):
        ck = SimpleCookie(chunk)
        assert len(ck) in (0, 1)
        if session_name in ck.keys():
            session_cookie = ck
            logger.debug(f"Found session cookie: {shorten(str(session_cookie), text_len)}")
            break
    if session_cookie is None:
        cookie_str = ""
    else:
        cookie_str = session_cookie.output().split('Set-Cookie: ')[1]
    logger.debug(f"Extracted session cookie string: {shorten(str(cookie_str), text_len)}")
    hdr = req.headers.copy()
    hdr['Cookie'] = cookie_str
    out = req.clone(headers=hdr)
    return out
