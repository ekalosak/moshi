# https://github.com/aiortc/aiortc/blob/main/examples/server/server.py
import argparse
import asyncio
import json
import os
import ssl
import uuid

# mine
import functools

from aiohttp import web
from aiortc import MediaStreamTrack, RTCPeerConnection, RTCSessionDescription
from aiortc.contrib.media import MediaBlackhole, MediaPlayer, MediaRecorder, MediaRelay

# mine
from loguru import logger

# mine
from server import util, audio

util.setup_loguru()

ROOT = os.path.dirname(__file__)
pcs = set()  # peer connections

async def index(request):
    """ HTTP endpoint for index.html """
    logger.info(request)
    content = open(os.path.join(ROOT, "index.html"), "r").read()
    return web.Response(content_type="text/html", text=content)

async def javascript(request):
    """ HTTP endpoint for client.js """
    content = open(os.path.join(ROOT, "client.js"), "r").read()
    return web.Response(content_type="application/javascript", text=content)

def async_with_pcid(f):
    """ Decorator for contextualizing the logger with a PeerConnection uid. """
    @functools.wraps(f)
    async def wrapped(*a, **k):
        pcid = uuid.uuid4()
        with logger.contextualize(PeerConnection=str(pcid)):
            return await f(*a, **k)
    return wrapped

@async_with_pcid
async def offer(request):
    """ In WebRTC, there's an initial offer->answer exchange that negotiates the connection parameters.
    This endpoint accepts an offer request from a client and returns an answer with the SDP (session description protocol).
    Moreover, it sets up the PeerConnection (pc) and the event listeners on the connection.
    """
    params = await request.json()
    logger.trace(f"request params: {params}")
    offer = RTCSessionDescription(sdp=params["sdp"], type=params["type"])

    pc = RTCPeerConnection()
    pcs.add(pc)
    logger.info(f"Created peer connection and offer for remote: {request.remote}")
    logger.trace(f"offer: {offer}")

    listener = audio.AudioListener()

    @pc.on("datachannel")
    def on_datachannel(channel):
        @channel.on("message")
        def on_message(message):
            if isinstance(message, str) and message.startswith("ping"):
                channel.send("pong" + message[4:])

    @pc.on("connectionstatechange")
    async def on_connectionstatechange():
        logger.info(f"Connection state is: {pc.connectionState}")
        if pc.connectionState == "failed":
            await pc.close()
            pcs.discard(pc)

    @pc.on("track")
    def on_track(track):
        logger.info(f"Track {track.kind} received")

        if track.kind != 'audio':
            raise TypeError(f"Track kind not supported, expected 'audio', got: '{track.kind}'")
            # TODO when debugged, only addTrack on kind == 'audio' and not this obverse
        listener.addTrack(track)

        @track.on("ended")
        async def on_ended():
            logger.info(f"Track {track.kind} ended")
            await listener.stop()

    await pc.setRemoteDescription(offer)

    # NOTE on_track should have been called by this point
    await listener.start()

    answer = await pc.createAnswer()
    await pc.setLocalDescription(answer)

    logger.trace(f"answer: {answer}")
    return web.Response(
        content_type="application/json",
        text=json.dumps(
            {"sdp": pc.localDescription.sdp, "type": pc.localDescription.type}
        ),
    )


async def on_shutdown(app):
    # close peer connections
    coros = [pc.close() for pc in pcs]
    await asyncio.gather(*coros)
    pcs.clear()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="WebRTC audio / data-channels demo"
    )
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
    app.on_shutdown.append(on_shutdown)
    app.router.add_get("/", index)
    app.router.add_get("/client.js", javascript)
    app.router.add_post("/offer", offer)
    web.run_app(
        app, access_log=None, host=args.host, port=args.port, ssl_context=ssl_context
    )
