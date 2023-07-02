from aiohttp import web, web_request
from loguru import logger

from moshi.server.util import require_authentication
from .. import util as sutil


@require_authentication
async def news(request: web_request.Request):
    logger.info(request)
    template = sutil.env.get_template("news.html")
    html = sutil.render(template, request)
    return web.Response(text=html, content_type="text/html")
