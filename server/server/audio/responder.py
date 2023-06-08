""" This module provides the ResponsePlayer class that plays audio responses to the remote client speakers. """
import asyncio
import os

from aiortc import MediaStreamTrack
from av import AudioFrame, AudioFifo
from loguru import logger

from server.audio import util

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
        frame = self.__fifo.read(FRAME_SIZE, partial=True)
        if frame is None:
            frame = util.empty_frame(FRAME_SIZE)
            self.__sent.set()  # frame is none means whatever audio was written is flushed
        # TODO throttle playback so the client buffer isn't overrun
        return frame

    def write_audio(self, af: AudioFrame):
        self.__fifo.write(af)
        self.__sent.clear()

class ResponsePlayer:
    """ When audio is set, it is sent over the track. """
    def __init__(self):
        self.__sent = asyncio.Event()  # set when the track plays all audio
        self.__track = ResponsePlayerStream(self.__sent)
        logger.info(f"Initialized player track: {util._track_str(self.__track)}")

    @property
    def audio(self):
        return self.__track

    async def send_utterance(self, af: AudioFrame):
        """ Flush the audio frame to the track and send it real-time then return.
        It's important that it be realtime because we need to be relatively on time for switching from listening to
        thinking and speaking.
        """
        self.__track.write_audio(af)
        frame_time = util.get_frame_seconds(af)
        timeout = frame_time + 1.
        print(f'responder frame_time={frame_time}, timeout={timeout}')
        try:
            await asyncio.wait_for(
                self.__sent.wait(),
                timeout = timeout,
            )
        except asyncio.TimeoutError:
            logger.debug(f"Timed out waiting for audio to be played, frame_time={frame_time} timeout={timeout}")
        except MediaStreamError:
            logger.error("MediaStreamError")
            raise
