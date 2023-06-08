""" This module provides the ResponsePlayer class that plays audio responses to the remote client speakers. """
import asyncio
import os
import time

from aiortc import MediaStreamTrack
from av import AudioFrame, AudioFifo
from loguru import logger

from server.audio import util

SAMPLE_RATE = int(os.getenv("MOSHISAMPLERATE", 44100))
FRAME_SIZE = int(os.getenv("MOSHIFRAMESIZE", 960))
assert FRAME_SIZE >= 128 and FRAME_SIZE <= 4096

class ResponsePlayerStream(MediaStreamTrack):
    kind = 'audio'
    def __init__(self, sent: asyncio.Event):
        super().__init__()
        self.__fifo = AudioFifo()
        self.__sent = sent
        self.__start_time = None
        self.__pts = 0

    async def recv(self) -> AudioFrame:
        """ Return audio from the fifo if it exists, otherwise return silence. """
        if self.__start_time is None:
            self.__start_time = time.monotonic()
        frame = self.__fifo.read(FRAME_SIZE, partial=False)
        if frame is None:
            self.__fifo.read(partial=True)  # drop any partial fragment
            frame = util.empty_frame(
                length=FRAME_SIZE,
                sample_rate=SAMPLE_RATE,
                pts=None,
            )
            self.__sent.set()  # frame is none means whatever audio was written is flushed
        frame.pts = self.__pts
        self.__pts += 1
        await self.__throttle_playback(frame)
        return frame

    async def __throttle_playback(self, frame: AudioFrame, max_buf_sec=.1):
        """ Ensure client buffer isn't overfull by sleeping until max_buf_sec before the frame should be played relative
        to the start of the stream. """
        current_time = time.monotonic()
        frame_start_time = self.__start_time + util.get_frame_start_time(frame)
        delay = frame_start_time - (current_time + max_buf_sec)
        delay = max(0., delay)
        await asyncio.sleep(delay)

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

    async def send_utterance(self, frame: AudioFrame):
        """ Flush the audio frame to the track and send it real-time then return.
        It's important that it be realtime because we need to be relatively on time for switching from listening to
        thinking and speaking.
        """
        self.__track.write_audio(frame)
        frame_time = util.get_frame_seconds(frame)
        timeout = frame_time + 1.
        logger.debug(f'responder frame_time={frame_time:.3f}, timeout={timeout:.3f}')
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
