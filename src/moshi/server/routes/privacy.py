from aiohttp import web, web_request
from loguru import logger

from .. import util as sutil

@require_authentication
async def privacy(request: web_request.Request):
    logger.info(request)
    template = sutil.env.get_template('privacy.html')
    html = template.render()
    return web.Response(text=html, content_type='text/html')

