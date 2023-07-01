from aiohttp import web, web_request

from moshi.server.util import require_authentication

@require_authentication
async def news(request: web_request.Request):
    logger.info(request)
    template = env.get_template('news.html')
    html = template.render()
    return web.Response(text=html, content_type='text/html')

