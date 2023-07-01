import functools

from .. import util as sutil

def async_with_pcid(f):
    """Decorator for contextualizing the logger with a PeerConnection uid."""

    @functools.wraps(f)
    async def wrapped(*a, **k):
        pcid = uuid.uuid4()
        with logger.contextualize(PeerConnection=str(pcid)):
            return await f(*a, **k)

    return wrapped

# Create WebRTC handler; offer/ is called by client.js on index.html having created an initial SDP offer;
@async_with_pcid
@sutil.require_authentication
async def offer(request):
    """In WebRTC, there's an initial offer->answer exchange that negotiates the connection parameters.
    This endpoint accepts an offer request from a client and returns an answer with the SDP (session description protocol).
    Moreover, it sets up the PeerConnection (pc) and the event listeners on the connection.
    Sources:
        - RFC 3264
        - RFC 2327
    """
    params = await request.json()
    logger.trace(f"Request params: {params}")
    session = await get_session(request)
    assert params["type"] == "offer", "At /offer endpoint, the SDP must be type 'offer'. Error in client.js."  # TODO make this 500 without crashing
    offer = RTCSessionDescription(sdp=params["sdp"], type=params["type"])
    logger.trace(f"offer: {offer}")
    # ice_config = await ice.get_ice_config(session['turn_token'])
    # pc = RTCPeerConnection(ice_config)
    pc = RTCPeerConnection()
    pcs.add(pc)
    logger.info(f"Created peer connection to: {request.remote}")

    usremail = session['user_email']  # pass so logging will record user email
    chatter = core.WebRTCChatter(usremail)

    with logger.contextualize(email=usremail):

        @pc.on("datachannel")
        def on_datachannel(channel: RTCDataChannel):
            if channel.label == "pingpong":
                @channel.on("message")
                def on_message(message):
                    if isinstance(message, str) and message.startswith("ping"):
                        channel.send("pong" + message[4:])  # NOTE io under the hood done with fire-and-forget ensure_future, UDP
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
                try:
                    await chatter.connected()
                except asyncio.TimeoutError as e:
                    logger.error("Timed out waiting for datachannels to be established.")

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

    return web.Response(
        content_type="application/json",
        text=json.dumps(
            {"sdp": pc.localDescription.sdp, "type": pc.localDescription.type}
        ),
    )

