# https://github.com/aiortc/aiortc/blob/main/examples/server/server.py
import argparse
import asyncio
import json
import os
import ssl
import uuid

# mine
from pprint import pformat
import functools
import sys

from aiohttp import web
from aiortc import MediaStreamTrack, RTCPeerConnection, RTCSessionDescription
from aiortc.contrib.media import MediaBlackhole, MediaPlayer, MediaRecorder, MediaRelay

# mine
from loguru import logger
from loguru._defaults import LOGURU_FORMAT
from speech_recognition import AudioSource
import speech_recognition as sr
import pyaudio

LOG_FORMAT = LOGURU_FORMAT + " | <g><d>{extra}</d></g>"
logger.remove()
logger.add(sink=sys.stderr, format=LOG_FORMAT, colorize=True)

ROOT = os.path.dirname(__file__)
pcs = set()  # peer connections
rec = sr.Recognizer()

class WebMicTrack(MediaStreamTrack):
    """
    An audio track that provides access to frames from a WebRTC track.
    Thin wrapper indicating source (WebMic) and kind (audio).
    """
    kind = 'audio'
    def __init__(self, track):
        super().__init__()
        self.track = track
    async def recv(self):
        return await self.track.recv()

class WebMicSource(AudioSource):
    """ This class does two important things:
    1. Adapt the async aiortc.MediaStreamTrack.recv() to a syncronous read()
    2. Adapt the av.AudioFrame unboxed from the MediaStreamTrack.recv() into bytes expected by the Recognizer.
    """
    def __init__(self, buf_track, fmt=pyaudio.paInt16):
        self.track = buf_track
        self.stream = None
        self.format = fmt
        self.CHUNK = 4096  # NOTE this must match the AudioFrame.frame_size
        self.SAMPLE_RATE = 44100
        # self.SAMPLE_WIDTH = 
    def __enter__(self):
        self.stream = WebMicSource.WebMicStream(self.track)
        return self
    def __exit__(self, extp, exval, tb):
        # TODO perhaps... close the stream..?
        self.stream = None

    class WebMicStream:
        def __init__(self, track, audio_format=None):
            assert audio_format is None, "not yet supported"
            # self.resampler = av.AudioResampler(
            #     format='s16',   # Specify the desired output format, e.g., signed 16-bit PCM
            #     layout='mono',  # Specify the desired output layout, e.g., mono
            #     rate=44100      # Specify the desired output sample rate, e.g., 44.1 kHz
            # )
            self.track = track
            self.timeout = 0.1

        def read(self, size: int) -> bytes:
            """ Adapts the async track.recv() to a synchronous call.
            FUTURE: The returned bytes adhere to the AudioSource constants (CHUNK, SAMPLE_RATE, and SAMPLE_WIDTH) via
            the resampler.
            Example usage: https://github.com/Uberi/speech_recognition/blob/master/speech_recognition/__init__.py#L198
            Args:
                - size: number of bytes to read off the buffer
            """
            co_frame = self.track.recv()  # coroutine
            # ev_loop = asyncio.get_event_loop()  # event loop
            # ft_frame = asyncio.ensure_future(co_frame)
            av_frame = asyncio.run(co_frame)
            # av_frame = ev_loop.run_until_complete(ft_frame)
            # av_frame = ft_frame.result(timeout=self.timeout)  # A[T] -> T
            pa_frame = util.pyav_audioframe_to_bytes(av_frame)  # av.AudioFrame -> bytes
            return pa_frame

async def index(request):
    logger.info(request)
    content = open(os.path.join(ROOT, "index.html"), "r").read()
    return web.Response(content_type="text/html", text=content)


async def javascript(request):
    content = open(os.path.join(ROOT, "client.js"), "r").read()
    return web.Response(content_type="application/javascript", text=content)

def async_with_pcid(f):
    """ Contextualize the logger with a PeerConnection uid. """
    @functools.wraps(f)
    async def wrapped(*a, **k):
        pcid = uuid.uuid4()
        with logger.contextualize(PeerConnection=str(pcid)):
            return await f(*a, **k)
    return wrapped

@async_with_pcid
async def offer(request):
    """ In WebRTC, there's an initial offer->answer exchange that negotiates the SDP (sess. desc. protoc.).
    This endpoint handles an offer request from a client and returns an answer with the SDP 
    """
    params = await request.json()
    logger.trace(f"request params: {params}")
    offer = RTCSessionDescription(sdp=params["sdp"], type=params["type"])

    pc = RTCPeerConnection()
    pcs.add(pc)
    logger.info(f"Created peer connection and offer for remote: {request.remote}")
    logger.trace(f"offer: {offer}")

    # prepare local media
    relay = MediaRelay()  # produces a buffered track that'll be wrapped in the WebMicTrack

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
        buf_track = relay.subscribe(track, buffered=True)
        logger.debug(f"Created buffered track: {buf_track}")
        webmic_track = WebMicTrack(buf_track)
        logger.debug(f"Created web mic track: {webmic_track}")
        audio_source = WebMicSource(webmic_track)
        logger.debug(f"Created audio source: {audio_source}")
        with audio_source as source:  # __enter__ initializes the stream
            logger.debug(f"Created audio stream: {source.stream}")
            audio = rec.listen(source)
        logger.success(f"Got audio: {audio}")
        transcript = rec.recognize_sphinx(audio)
        logger.info(f"Got transcript: {transcript}")

        @track.on("ended")
        async def on_ended():
            logger.info(f"Track {track.kind} ended")
            # await recorder.stop()  # TODO stop the ... track?

    # handle offer
    await pc.setRemoteDescription(offer)
    # await recorder.start()

    # send answer
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
