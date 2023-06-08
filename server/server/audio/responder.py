""" This module provides the ResponsePlayer class that plays audio responses to the remote client speakers. """
import asyncio

from aiortc import MediaStreamTrack
from av import AudioFrame, AudioFifo
from loguru import logger

from server.audio.util import _track_str

FRAME_SIZE = int(os.getenv("MOSHIFRAMESIZE", 960))
assert FRAME_SIZE >= 128 and FRAME_SIZE <= 4096

class ResponsePlayerStream(MediaStreamTrack):
    kind = 'audio'
    def __init__(self, sent: asyncio.Event):
        super().__init__()
        self.__fifo = AudioFifo()
        self.__sent = sent

    async def recv(self) -> AudioFrame:
        """ Return audio from the fifo if it exists, otherwise return silence. """
        while frame := self.__fifo.read(FRAME_SIZE, partial=False) is None:
            ef = util.empty_frame(FRAME_SIZE)
            self.__fifo.write(ef)
        # TODO notify sent when the fifo is empty of non-silent audio
        # TODO throttle playback so the client buffer isn't overrun
        return frame

class ResponsePlayer:
    """ When audio is set, it is sent over the track. """
    def __init__(self):
        self.__sent = asyncio.Event()
        self.__track = ResponsePlayerStream(self.__sent)
        logger.info(f"Initialized player track: {_track_str(self.__track)}")

    @property
    def audio(self):
        return self.__track
