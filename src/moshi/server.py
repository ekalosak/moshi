import asyncio
import glob
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
import jinja2
from loguru import logger

import moshi
from moshi import secrets, core, gcloud, lang, speech, util, AuthenticationError

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
# with open('secret/client_id', 'r') as f:
#     CLIENT_ID = f.read().strip()
SECURE_COOKIE = not NO_SECURITY
if not SECURE_COOKIE:
    logger.warning(f"SECURE_COOKIE={SECURE_COOKIE}")
else:
    logger.info(f"SECURE_COOKIE={SECURE_COOKIE}")
# NOTE DEBUG cloud deployment secret injection
# with open('secret/user-whitelist.csv', 'r') as f:
#     whitelisted_emails = [em.strip() for em in f.readlines()]
whitelisted_emails = ["helloateric@gmail.com", "JKenyon@umich.edu", "Triciak@umich.edu", "benkalosakenyon@gmail.com", "natekenyon3@gmail.com", "leahpom@gmail.com"]
whitelisted_emails = [em.lower() for em in whitelisted_emails]
_es = '\n\t'.join(whitelisted_emails)  # note, \ not allowed in f-string {} terms
logger.info(f"Allowed users:\n\t{_es}")

# DEBUG print files
_files = [Path(p).name for p in Path(ROOT).iterdir()]
_files = ", ".join(_files)
logger.debug(f"ROOT={ROOT} contains: {_files}")

# Setup global objects
pcs = set()
env = jinja2.Environment(
    loader=jinja2.FileSystemLoader(ROOT),
    autoescape=jinja2.select_autoescape(['html', 'xml']),
)
logger.info("Setup peer connection tracker and html templating engine.")

# Define HTTP endpoints and tooling for authentication
async def login(request: web_request.Request):
    """HTTP GET endpoint for login.html"""
    logger.info(request)
    error_message = request.query.get('error', '')
    template = env.get_template('templates/login.html')
    origin = request.url.origin()
    logger.debug(f"request origin: {str(origin)}")
    scheme = 'https' if HTTPS else 'http'
    if scheme == 'http':
        logger.warning("Using HTTP, no SSL - insecure!")
    # NOTE for google login button to appear, login_uri must be https on public site "[GSI_LOGGER]: Error parsing
    # configuration from HTML: Unsecured login_uri provided. client:44:322" otherwise;
    login_uri = request.url.with_scheme(scheme)
    logger.debug(f"Using login_uri for Google auth: {login_uri}")
    html = template.render(
        client_id=CLIENT_ID,
        login_uri=login_uri,
        error=error_message,
    )
    return web.Response(text=html, content_type='text/html')

def _handle_auth_error(e: AuthenticationError):
    """Raise the AuthenticationError to the user, redirecting them to the login page."""
    err_str = str(e)
    logger.debug(f"Presenting err_str to user: {err_str}")
    err_str = urllib.parse.quote(err_str)
    raise web.HTTPFound(f"/login?error={err_str}")

async def login_callback(request):
    """HTTP POST endpoint for handling Google OAuth 2.0 callback i.e. after user logs in.
    Sets up the user session, then redirects to main page.
    """
    logger.info(request)
    session = await new_session(request)
    data = await request.post()
    token = data['credential']
    try:
        id_info = id_token.verify_oauth2_token(token, requests.Request())
        if id_info['iss'] not in ALLOWED_ISS:
            raise AuthenticationError('Authentication failed')
        user_email = id_info['email'].lower()
        logger.debug(f'user_email={user_email}')
        if user_email not in whitelisted_emails:
            raise AuthenticationError('Unrecognized user')
        user_id = id_info['sub']
        session['user_id'] = user_id
        session['user_given_name'] = id_info['given_name']
        session['user_email'] = user_email
        session.set_new_identity(user_id)
        # TODO make sure the user email is verified id_info['email_verified']
        logger.debug(f"Authentication successful for user: {user_email}")
        raise web.HTTPFound('/')
    except AuthenticationError as e:
        logger.error(f"Authentication failed: {e}")
        _handle_auth_error(e)

def require_authentication(http_endpoint_handler):
    """Decorate an HTTP endpoint so it requires auth."""
    async def auth_wrapper(request):
        logger.debug(f"Checking authentication for page '{request.path}'")
        request = util.remove_non_session_cookies(request, COOKIE_NAME)  # NOTE because google's cookie is unparsable by http.cookies
        session = await get_session(request)
        user_email = session.get('user_email')
        logger.debug(f"Checking authentication for user_email: {user_email}")
        try:
            if user_email is None:
                logger.debug("No user_email in session cookie, user not logged in.")
                raise web.HTTPFound(f"/login")
            if user_email not in whitelisted_emails:
                raise AuthenticationError(f"Unrecognized user: {user_email}")
        except AuthenticationError as e:
            _handle_auth_error(e)
        logger.debug(f"User {user_email} is authenticated!")
        return await http_endpoint_handler(request)
    return auth_wrapper

# Define application HTTP endpoints
@require_authentication
async def index(request):
    """HTTP endpoint for index.html"""
    logger.info(request)
    template = env.get_template('templates/index.html')
    html = template.render(version=f"alpha-{moshi.__version__}")
    return web.Response(text=html, content_type="text/html")

# Define resource HTTP endpoints
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


# Create WebRTC handler
@util.async_with_pcid
async def offer(request):
    """In WebRTC, there's an initial offer->answer exchange that negotiates the connection parameters.
    This endpoint accepts an offer request from a client and returns an answer with the SDP (session description protocol).
    Moreover, it sets up the PeerConnection (pc) and the event listeners on the connection.
    """
    params = await request.json()
    logger.trace(f"Request params: {params}")
    offer = RTCSessionDescription(sdp=params["sdp"], type=params["type"])

    rtc_config = _make_rtc_config()
    pc = RTCPeerConnection()
    pcs.add(pc)
    logger.info(f"Created peer connection and offer for remote: {request.remote}")
    logger.trace(f"offer: {offer}")

    chatter = core.WebRTCChatter()

    @pc.on("datachannel")
    def on_datachannel(channel: RTCDataChannel):
        if channel.label == "pingpong":
            @channel.on("message")
            def on_message(message):
                if isinstance(message, str) and message.startswith("ping"):
                    channel.send("pong" + message[4:])  # NOTE blocking io
        else:
            chatter.add_channel(channel)

    @pc.on("connectionstatechange")
    async def on_connectionstatechange():
        logger.info(f"Connection state changed to: {pc.connectionState}")
        if pc.connectionState == "failed":
            await pc.close()
            pcs.discard(pc)
        elif pc.connectionState == "connecting":
            # on_track should have been called by this point, so start should be ok
            await chatter.start()
        elif pc.connectionState == "connected":
            await chatter.connected()

    @pc.on("track")
    def on_track(track):
        logger.info(f"Track {track.kind} received")
        if track.kind != "audio":
            raise TypeError(
                f"Track kind not supported, expected 'audio', got: '{track.kind}'"
            )
        chatter.detector.setTrack(track)  # must be called before start()
        pc.addTrack(chatter.responder.audio)

        @track.on("ended")
        async def on_ended():  # e.g. user disconnects audio
            await chatter.stop()
            logger.info(f"Track {track.kind} ended")

    # on_track gets called when the remote description is set, I think
    await pc.setRemoteDescription(offer)

    answer = await pc.createAnswer()
    logger.trace(f"answer: {answer}")
    await pc.setLocalDescription(answer)

    return web.Response(
        content_type="application/json",
        text=json.dumps(
            {"sdp": pc.localDescription.sdp, "type": pc.localDescription.type}
        ),
    )


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
    lang._setup_client()  # doing this here to avoid waiting when first request happens
    speech._setup_client()
    secrets._setup_client()
    logger.info("API clients created.")
    logger.success("Set up!")

@logger.catch
def make_app() -> 'web.Application':
    """Initialize the """
    app = web.Application()
    if SECURE_COOKIE:
        secret_key = os.urandom(32)
        # with open('secret/session_cookie_key_32', 'rb') as f:
        #     secret_key = f.read()
        cookie_storage = EncryptedCookieStorage(secret_key, cookie_name=COOKIE_NAME)
    else:
        cookie_storage = SimpleCookieStorage(cookie_name=COOKIE_NAME)
        logger.warning("Using insecure cookie storage")
    session_setup(app, cookie_storage)
    app.on_shutdown.append(on_shutdown)
    app.on_startup.append(on_startup)
    app.router.add_get("/", index)
    app.router.add_get("/login", login)
    app.router.add_post("/login", login_callback)
    app.router.add_get("/favicon.ico", favicon)
    app.router.add_get("/client.js", javascript)
    app.router.add_get("/style.css", css)
    app.router.add_post("/offer", offer)
    return app
