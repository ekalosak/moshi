from aiohttp_session import get_session, new_session, setup as session_setup, SimpleCookieStorage

from ..util import require_authentication

@require_authentication
async def index(request):
    """HTTP endpoint for index.html"""
    logger.info(request)
    session = await get_session(request)
    template = env.get_template("index.html")
    html = sutil.render(template, request)
    return web.Response(text=html, content_type="text/html")


