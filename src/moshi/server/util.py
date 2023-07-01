import os
from pathlib import Path

import jinja2
from loguru import logger

from moshi import __version__, util

NO_SECURITY = bool(os.getenv("MOSHINOSECURITY", False))
if NO_SECURITY:
    logger.warning(f"NO_SECURITY={NO_SECURITY}")
HTTPS = not NO_SECURITY
if not HTTPS:
    logger.warning(f"HTTPS={HTTPS}")

TEMPLATE_DIR = Path(__file__).parent / 'templates'

env = jinja2.Environment(
    loader=jinja2.FileSystemLoader(TEMPLATE_DIR),
    autoescape=jinja2.select_autoescape(['html', 'xml']),
)

def render(template, request, **kwargs) -> 'html':
    """Add default routes to template from request.app.router; pass kwg to template.render()"""
    index_url = str(request.app.router['index'].url_for())
    news_url = str(request.app.router['news'].url_for())
    privacy_url = str(request.app.router['privacy'].url_for())
    html = template.render(
        version=f"alpha-{__version__}",
        index_url=index_url,
        news_url=news_url,
        privacy_url=privacy_url,
        **kwargs
    )
    return html

def require_authentication(http_endpoint_handler):
    """Decorate an HTTP endpoint so it requires auth."""
    async def auth_wrapper(request):
        logger.debug(f"Checking authentication for page '{request.path}'")
        request = util.remove_non_session_cookies(request, COOKIE_NAME)  # NOTE because google's cookie is unparsable by http.cookies
        session = await get_session(request)
        user_email = session.get('user_email')
        logger.debug(f"Checking authentication for user_email: {user_email}")
        if user_email is None:
            logger.debug("No user_email in session cookie, user not logged in.")
            raise web.HTTPFound(f"/login")
        logger.debug(f"User {user_email} is authenticated!")
        return await http_endpoint_handler(request)
    return auth_wrapper
