from aiohttp import web, web_request
from aiohttp_session import new_session
from google.oauth2 import id_token
from google.auth.transport import requests as google_requests
from loguru import logger

from moshi import auth, UserAuthenticationError
from moshi.server import util as sutil

async def signup(request: web_request.Request):
    """HTTP GET endpoint for login.html"""
    logger.info(request)
    template = sutil.env.get_template("signup.html")
    scheme = "https" if sutil.HTTPS else "http"
    if scheme == "http":
        logger.warning("Using HTTP, no SSL - insecure!")
    html = sutil.render(
        template,
        request,
        client_id=sutil.CLIENT_ID,
    )
    return web.Response(text=html, content_type="text/html")
