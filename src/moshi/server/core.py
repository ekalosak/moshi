"""Main module, used to assemble the server components and routes.
See app/main.py for usage example.
"""
import asyncio
import json
import os
from pathlib import Path
import ssl
import urllib.parse

from aiohttp import web, web_request
from aiohttp_session import get_session, new_session, setup as session_setup, SimpleCookieStorage
from aiohttp_session.cookie_storage import EncryptedCookieStorage
from aiortc import RTCPeerConnection, RTCSessionDescription, RTCDataChannel
from google.oauth2 import id_token
from google.auth.transport import requests
from loguru import logger

import moshi
from moshi import auth, secrets, core, gcloud, lang, speech, think, util
from . import util as sutil
from .routes.healthz import healthz
from .routes.login import login, login_callback
from .routes.news import news
from .routes.privacy import privacy

NO_SECURITY = bool(os.getenv("MOSHINOSECURITY", False))
if NO_SECURITY:
    logger.warning(f"NO_SECURITY={NO_SECURITY}")
HTTPS = not NO_SECURITY
if not HTTPS:
    logger.warning(f"HTTPS={HTTPS}")

# Setup constants
ROOT = os.path.dirname(__file__)
ALLOWED_ISS = ['accounts.google.com', 'https://accounts.google.com']
COOKIE_NAME = "MOSHI-002"
# Client id is for Google OAuth2
CLIENT_ID = "462213871057-tsn4b76f24n40i7qrdrhflc7tp5hdqu2.apps.googleusercontent.com"
SESSION_KEY_SECRET_ID = "session-key-001"  # for HTTP cookie encryption
logger.info(f"Using SESSION_KEY_SECRET_ID={SESSION_KEY_SECRET_ID}")
SECURE_COOKIE = not NO_SECURITY
if not SECURE_COOKIE:
    logger.warning(f"SECURE_COOKIE={SECURE_COOKIE}")
else:
    logger.info(f"SECURE_COOKIE={SECURE_COOKIE}")

# Setup global objects
pcs = set()
logger.info("Setup peer connection tracker and html templating engine.")

async def favicon(request):
    """HTTP endpoint for the favicon"""
    fp = os.path.join(ROOT, "static/favicon.ico")
    return web.FileResponse(fp)


async def css(request):
    """HTTP endpoint for style.css"""
    content = open(os.path.join(ROOT, "static/style.css"), "r").read()
    return web.Response(content_type="text/css", text=content)


@require_authentication
async def javascript(request):
    """HTTP endpoint for client.js"""
    content = open(os.path.join(ROOT, "static/client.js"), "r").read()
    return web.Response(content_type="application/javascript", text=content)



@logger.catch
async def on_shutdown(app):
    logger.info(f"Shutting down {len(pcs)} PeerConnections...")
    # close peer connections
    coros = [pc.close() for pc in pcs]
    await asyncio.gather(*coros)
    pcs.clear()
    logger.success("Shut down gracefully!")

@logger.catch
async def on_startup(app):
    """Setup the state monad."""
    logger.debug("Setting up logger...")
    util._setup_loguru()
    logger.info("Logger set up.")
    logger.debug("Setting up error handler...")
    asyncio.get_event_loop().set_exception_handler(util.aio_exception_handler)
    logger.info("Error handler set up.")
    logger.debug("Authenticating to Google Cloud...")
    await gcloud.authenticate()
    logger.info(f"Authenticated to Google Cloud.")
    logger.debug("Creating API clients...")
    auth._setup_client()
    lang._setup_client()  # doing this here to avoid waiting when first request happens
    speech._setup_client()
    secrets._setup_client()
    logger.info("API clients created.")
    logger.debug("Setting up OpenAI...")
    await think._setup_api_key()
    logger.info("OpenAI setup complete.")
    logger.success(f"Set up moshi version: {moshi.__version__}")

@logger.catch
async def make_app() -> 'web.Application':
    """Initialize the """
    app = web.Application()
    if SECURE_COOKIE:
        secret_key = await secrets.get_secret(SESSION_KEY_SECRET_ID, decode=None)
        # secret_key = os.urandom(32)
        cookie_storage = EncryptedCookieStorage(secret_key, cookie_name=COOKIE_NAME)
        logger.success("Setup encrypted cookie storage.")
    else:
        cookie_storage = SimpleCookieStorage(cookie_name=COOKIE_NAME)
        logger.warning("Using insecure cookie storage.")
    session_setup(app, cookie_storage)
    app.on_shutdown.append(on_shutdown)
    app.on_startup.append(on_startup)
    app.router.add_get("/", index, name="index")
    app.router.add_get("/healthz", healthz, name="health")
    app.router.add_get("/privacy", privacy, name="privacy")
    app.router.add_get("/news", news, name="news")
    app.router.add_get("/login", login, name="login")
    app.router.add_post("/login", login_callback)
    app.router.add_get("/favicon.ico", favicon)
    app.router.add_get("/client.js", javascript)
    app.router.add_get("/style.css", css)
    app.router.add_post("/offer", offer)
    return app
