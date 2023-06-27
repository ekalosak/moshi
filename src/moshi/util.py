import asyncio
import functools
from http.cookies import SimpleCookie
import os
import sys
from textwrap import shorten
import uuid
import warnings

from google.cloud import logging
from google.protobuf.json_format import ParseError
from loguru import logger
from loguru._defaults import LOGURU_FORMAT
import pyfiglet

FILE_LOGS = bool(os.getenv("MOSHILOGDISK", 0))
STDOUT_LOGS = bool(os.getenv("MOSHILOGSTDOUT", 1))
CLOUD_LOGS = bool(os.getenv("MOSHILOGCLOUD", 0))

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

def _format_timedelta(td) -> str:
    return f"{td.days}days{td.seconds}secs{td.microseconds}usecs"

def _to_log_dict(rec: dict) -> dict:
    """Convert a loguru record to a gcloud structured logging payload."""
    severity = _gcp_log_severity_map(rec["level"].name)
    rec.pop('level')
    if not rec['extra']:
        rec.pop('extra')
    rec['elapsed'] = _format_timedelta(rec['elapsed'])
    if rec['exception'] is not None:
        rec['exception'] = str(rec['exception'])
    else:
        rec.pop('exception')
    rec['file'] = rec['file'].name  # also .path
    rec['process_id'] = rec['process'].id
    rec['process_name'] = rec['process'].name
    rec.pop('process')
    rec['thread_id'] = rec['thread'].id
    rec['thread_name'] = rec['thread'].name
    rec.pop('thread')
    rec['timestamp'] = str(rec['time'])
    rec.pop('time')
    return rec

def _setup_loguru():
    # Loguru
    logger.level("INSTRUCTION", no=15, color="<light-yellow><bold>")
    logger.level("SPLASH", no=13, color="<light-magenta><bold>")
    logger.remove()
    log_format = LOGURU_FORMAT + " | <g><d>{extra}</d></g>"
    if STDOUT_LOGS:
        logger.add(
            sink=sys.stderr,
            level="DEBUG",
            format=log_format,
            colorize=True,
        )
    if FILE_LOGS:
        logger.add(
            "logs/server.log",
            level="DEBUG",
            format=log_format,
            rotation="10 MB",
        )
    # Google logging  (https://github.com/Delgan/loguru/issues/789)
    if CLOUD_LOGS:
        logging_client = logging.Client()
        gcp_logger = logging_client.logger("gcp-logger")
        def log_to_gcp(message):
            logdict = _to_log_dict(message.record)
            gcp_logger.log_struct(logdict)
        logger.add(
            sink=log_to_gcp,
            level="DEBUG",
            format="{message}",
        )

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
