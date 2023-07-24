import asyncio
import functools
import json
import os
import uuid

from aiohttp import web
from aiohttp_session import get_session
from aiortc import RTCPeerConnection, RTCSessionDescription, RTCDataChannel
from loguru import logger

from moshi.chat import WebRTCChatter
from moshi import util

pcs = set()

CONNECTION_TIMEOUT = int(os.getenv("MOSHICONNECTIONTIMEOUT", 5))
logger.info(f"Using (WebRTC session) CONNECTION_TIMEOUT={CONNECTION_TIMEOUT}")

def async_with_pcid(f):
    """Decorator for contextualizing the logger with a PeerConnection uid."""

    @functools.wraps(f)
    async def wrapped(*a, **k):
        pcid = uuid.uuid4()
        with logger.contextualize(PeerConnection=str(pcid)):
            return await f(*a, **k)

    return wrapped


async def shutdown():
    """Close peer connections."""
    logger.debug(f"Closing {len(pcs)} PeerConnections...")
    coros = [pc.close() for pc in pcs]
    await asyncio.gather(*coros)
    pcs.clear()


# Create WebRTC handler; offer/ is called by client.js on index.html having created an initial SDP offer;
@async_with_pcid
# NOTE DEBUG auth disabled for local dev.
# @util.require_authentication  # TODO use Firebase auth
async def offer(request):
    """In WebRTC, there's an initial offer->answer exchange that negotiates the connection parameters.
    This endpoint accepts an offer request from a client and returns an answer with the SDP (session description protocol).
    Moreover, it sets up the PeerConnection (pc) and the event listeners on the connection.
    Sources:
        - RFC 3264
        - RFC 2327
    """
    logger.info("Got offer")
    logger.debug(f"request: {request}")
    try:
        params = await request.json()
    except json.decoder.JSONDecodeError as e:
        logger.error("Invalid JSON: {e}")
        logger.debug(f"Response text: {response.text}")
        raise web.HTTPUnprocessableEntity(reason="Invalid JSON")
    logger.trace(f"Request params: {params}")
    # session = await get_session(request)
    if _tp := params.get("type") != "offer":
        err = f"Invalid offer type, expected 'offer', got: '{_tp}'"
        logger.error(err)
        raise web.HTTPBadRequest(reason = err)
    offer = RTCSessionDescription(sdp=params["sdp"], type=params["type"])
    logger.trace(f"offer: {offer}")
    pc = RTCPeerConnection()
    pcs.add(pc)
    logger.info(f"Created peer connection object for: {request.remote}")

    # usremail = session["user_email"]  # pass so logging will record user email
    usremail = "NONE - TEST"
    chatter = WebRTCChatter(usremail)

    with logger.contextualize(email=usremail):

        @pc.on("datachannel")
        def on_datachannel(dc: RTCDataChannel):
            logger.debug(f"dc: {dc}")
            logger.info(f"dc received: {dc.label}:{dc.id}")
            chatter.add_dc(dc)

            @dc.on("message")
            def on_message(msg):
                logger.debug(f'dc: msg: {msg}')
                if isinstance(msg, str) and msg.startswith("ping "):
                    # NOTE io under the hood done with fire-and-forget ensure_future, UDP
                    dc.send("pong " + msg[4:])

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
                try:
                    await asyncio.wait_for(chatter.wait_dc_connected(), timeout=CONNECTION_TIMEOUT)
                except asyncio.TimeoutError as e:
                    with logger.contextualize(timeout_sec=CONNECTION_TIMEOUT):
                        logger.error("Timeout waiting for dc connected")

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

    await pc.setRemoteDescription(offer)

    answer = await pc.createAnswer()
    logger.trace(f"answer: {answer}")
    await pc.setLocalDescription(answer)

    # NOTE DEBUG SO WE CAN SEE THE APP RING FOR A MOMENT
    await asyncio.sleep(1.0)
    return web.Response(
        content_type="application/json",
        text=json.dumps(
            {"sdp": pc.localDescription.sdp, "type": pc.localDescription.type}
        ),
    )
