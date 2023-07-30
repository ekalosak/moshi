""" This module provides the ResponsePlayer class that plays audio responses to the remote client speakers. """
import asyncio
import os
import time
from typing import Callable

from aiortc import MediaStreamTrack
from av import AudioFifo, AudioFrame
from loguru import logger

from moshi import AUDIO_FORMAT, AUDIO_LAYOUT, SAMPLE_RATE, audio

FRAME_SEND_TIMEOUT_SEC = 0.5  # how long beyond the length of the response to wait.
FRAME_SIZE = 960
assert FRAME_SIZE >= 128 and FRAME_SIZE <= 4096
logger.info(f"Using transport frame size: {FRAME_SIZE}")

logger.success("Loaded!")


class ResponsePlayerStream(MediaStreamTrack):
    kind = "audio"

    def __init__(self):
        super().__init__()
        self.__fifo = AudioFifo()
        self.__sent = asyncio.Event()

    async def recv(self) -> AudioFrame:
        """Return audio from the fifo whenever it exists, otherwise wait for it.
        """
        frame = None
        while frame == None:
            frame = self.__fifo.read(FRAME_SIZE, partial=True)
            if not frame:
                self.__sent.set()
                await asyncio.sleep(0.01)
        return frame

    async def send_audio(self, frame: AudioFrame):
        frame.pts = self.__fifo.samples_written
        self.__fifo.write(frame)
        await self.__sent.wait()
        self.__sent.clear()


class ResponsePlayer:
    """When audio is set, it is sent over the track."""

    def __init__(self):
        self.__track = ResponsePlayerStream()

    @property
    def audio(self):
        return self.__track

    async def send_utterance(self, frame: AudioFrame):
        """Write the frame to the audio track, thereby sending it to the remote client.
        Raises:
            - aiortc.MediaStreamError if the remote client hangs up.
            - asyncio.TimeoutError if the audio track is busy for longer than: FRAME_SEND_TIMEOUT_SEC.
        """
        assert frame.rate == SAMPLE_RATE
        timeout = audio.get_frame_seconds(frame) + FRAME_SEND_TIMEOUT_SEC
        await asyncio.wait_for(
            self.__track.send_audio(frame),
            timeout=timeout,
        )