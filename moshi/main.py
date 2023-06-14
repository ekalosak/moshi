import argparse
import asyncio
import json
import os
import ssl

from aiohttp import web
import aiohttp_session
from aiohttp_session.cookie_storage import EncryptedCookieStorage
from aiortc import RTCPeerConnection, RTCSessionDescription
from google.oauth2 import id_token
from google.auth.transport import requests
from loguru import logger

from moshi import core, gcloud, lang, speech, util

ROOT = os.path.dirname(__file__)
pcs = set()  # peer connections

async def login(request):
    """HTTP GET endpoint for login.html"""
    logger.info(request)
    content = open(os.path.join(ROOT, "web/resources/login.html"), "r").read()
    return web.Response(content_type="text/html", text=content)

async def login_callback(request):
    """HTTP POST endpoint for handling Google OAuth 2.0 callback i.e. after user logs in.
    Sets up the user session, then redirects to main page.
    """
    logger.info(request)
    data = await request.post()
    token = data['credential']
    try:
        id_info = id_token.verify_oauth2_token(token, requests.Request())
        if id_info['iss'] not in ['accounts.google.com', 'https://accounts.google.com']:
            raise ValueError('Invalid token')
        # Generate a session token and store it in the session storage
        session = await aiohttp_session.get_session(request)
        session['user_id'] = id_info['sub']  # Store the user ID in the session
        # TODO redirect to moshi
        return web.json_response({'message': 'Authentication successful'})
    except ValueError:
        return web.json_response({'message': 'Authentication failed'})

async def index(request):
    """HTTP endpoint for index.html"""
    logger.info(request)
    content = open(os.path.join(ROOT, "web/resources/index.html"), "r").read()
    return web.Response(content_type="text/html", text=content)


async def favicon(request):
    """HTTP endpoint for the favicon"""
    fp = os.path.join(ROOT, "web/resources/favicon.ico")
    return web.FileResponse(fp)


async def css(request):
    """HTTP endpoint for style.css"""
    content = open(os.path.join(ROOT, "web/resources/style.css"), "r").read()
    return web.Response(content_type="text/css", text=content)


async def javascript(request):
    """HTTP endpoint for client.js"""
    content = open(os.path.join(ROOT, "web/resources/client.js"), "r").read()
    return web.Response(content_type="application/javascript", text=content)


@util.async_with_pcid
async def offer(request):
    """In WebRTC, there's an initial offer->answer exchange that negotiates the connection parameters.
    This endpoint accepts an offer request from a client and returns an answer with the SDP (session description protocol).
    Moreover, it sets up the PeerConnection (pc) and the event listeners on the connection.
    """
    params = await request.json()
    logger.debug(f"request params: {params}")
    offer = RTCSessionDescription(sdp=params["sdp"], type=params["type"])

    pc = RTCPeerConnection()
    pcs.add(pc)
    logger.info(f"Created peer connection and offer for remote: {request.remote}")
    logger.debug(f"offer: {offer}")

    chatter = core.WebRTCChatter()

    @pc.on("datachannel")
    def on_datachannel(channel):
        if channel.label == "keepalive":

            @channel.on("message")
            def on_message(message):
                if isinstance(message, str) and message.startswith("ping"):
                    channel.send("pong" + message[4:])

        elif channel.label == "utterance":
            chatter.set_utterance_channel(channel)
        else:
            raise ValueError(f"Got unknown channel: {channel.label}")

    @pc.on("connectionstatechange")
    async def on_connectionstatechange():
        logger.info(f"Connection state is: {pc.connectionState}")
        if pc.connectionState == "failed":
            await pc.close()
            pcs.discard(pc)

    @pc.on("track")
    def on_track(track):
        logger.info(f"Track {track.kind} received")
        if track.kind != "audio":
            raise TypeError(
                f"Track kind not supported, expected 'audio', got: '{track.kind}'"
            )

        # This is how input and output are connected to the chatter
        chatter.detector.setTrack(track)  # must be called before start()
        pc.addTrack(chatter.responder.audio)

        @track.on("ended")
        async def on_ended():  # e.g. user disconnects audio
            await chatter.stop()
            logger.info(f"Track {track.kind} ended")

    # on_track gets called when the remote description is set, I think
    await pc.setRemoteDescription(offer)

    # on_track should have been called by this point, so start should be ok
    await chatter.start()

    answer = await pc.createAnswer()
    logger.debug(f"answer: {answer}")
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
    logger.debug("Setting up logging and error handler...")
    asyncio.get_event_loop().set_exception_handler(util.aio_exception_handler)
    logger.debug("Authenticating to Google Cloud...")
    await gcloud.authenticate()
    logger.info(f"Authenticated to Google Cloud.")
    logger.debug("Creating API clients...")
    lang._setup_client()  # doing this here to avoid waiting when first request happens
    speech._setup_client()
    logger.info("API clients created.")
    logger.success("Set up!")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Moshi web app")
    parser.add_argument("--cert-file", help="SSL certificate file (for HTTPS)")
    parser.add_argument("--key-file", help="SSL key file (for HTTPS)")
    parser.add_argument(
        "--host", default="127.0.0.1", help="Host for HTTP server (default: 127.0.0.1)"
    )
    parser.add_argument(
        "--port", type=int, default=5000, help="Port for HTTP server (default: 5000)"
    )
    args = parser.parse_args()

    if args.cert_file:
        ssl_context = ssl.SSLContext()
        ssl_context.load_cert_chain(args.cert_file, args.key_file)
    else:
        ssl_context = None

    app = web.Application()
    secret_key = os.urandom(32)
    aiohttp_session.setup(app, EncryptedCookieStorage(secret_key))
    app.on_shutdown.append(on_shutdown)
    app.on_startup.append(on_startup)
    app.router.add_get("/", index)
    app.router.add_get("/login", login)
    app.router.add_post("/login", login_callback)
    app.router.add_get("/favicon.ico", favicon)
    app.router.add_get("/client.js", javascript)
    app.router.add_get("/style.css", css)
    app.router.add_post("/offer", offer)
    web.run_app(
        app, access_log=None, host=args.host, port=args.port, ssl_context=ssl_context
    )
