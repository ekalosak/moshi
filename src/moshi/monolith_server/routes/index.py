from aiohttp import web
from aiohttp_session import (
    get_session,
    new_session,
    setup as session_setup,
    SimpleCookieStorage,
)
from loguru import logger

from .. import util as sutil


@sutil.require_authentication
async def index(request):
    """HTTP endpoint for index.html"""
    logger.info(request)
    session = await get_session(request)
    template = sutil.env.get_template("index.html")
    html = sutil.render(template, request)
    return web.Response(text=html, content_type="text/html")
