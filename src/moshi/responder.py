""" This module provides the ResponsePlayer class that plays audio responses to the remote client speakers. """
import asyncio
import os
import time
from typing import Callable

from aiortc import MediaStreamTrack
from aiortc.mediastreams import MediaStreamError
from av import AudioFifo, AudioFrame
from loguru import logger

from moshi import AUDIO_FORMAT, AUDIO_LAYOUT, SAMPLE_RATE, audio

FRAME_SIZE = int(os.getenv("MOSHIFRAMESIZE", 960))
assert FRAME_SIZE >= 128 and FRAME_SIZE <= 4096
logger.info(f"Using transport frame size: {FRAME_SIZE}")

logger.success("Loaded!")


class ResponsePlayerStream(MediaStreamTrack):
    kind = "audio"

    def __init__(self, sent: asyncio.Event):
        super().__init__()
        self.__fifo = AudioFifo()
        self.__sent = sent
        self.__start_time = None
        self.__pts = 0
        # For not flooding traces:
        self.__throttled_first_playback = False

    async def recv(self) -> AudioFrame:
        """Return audio from the fifo if it exists, otherwise return silence.
        This track should never raise a MediaStreamError.
        """
        frame = self.__fifo.read(FRAME_SIZE, partial=False)
        if frame is None:
            self.__fifo.read(partial=True)  # drop any partial fragment
            frame = audio.empty_frame(
                length=FRAME_SIZE,
                rate=SAMPLE_RATE,
                format=AUDIO_FORMAT,
                layout=AUDIO_LAYOUT,
                pts=None,
            )
            self.__sent.set()  # frame is none means whatever audio was written is flushed
        frame.pts = self.__pts
        self.__pts += frame.samples
        await self.__throttle_playback(frame)
        return frame

    async def __throttle_playback(self, frame: AudioFrame, max_buf_sec=0.1):
        """Ensure client buffer isn't overfull by sleeping until max_buf_sec before the frame should be played relative
        to the start of the stream."""
        if self.__start_time is None:
            self.__start_time = time.monotonic()
        current_time = time.monotonic()
        frame_start_time = self.__start_time + audio.get_frame_start_time(frame)
        delay = frame_start_time - (current_time + max_buf_sec)
        delay = max(0.0, delay)
        if not self.__throttled_first_playback:
            logger.trace(f"Throttling playback, sleeping for delay={delay:.3f} sec")
            self.__throttled_first_playback = True
        await asyncio.sleep(delay)

    def write_audio(self, frame: AudioFrame):
        logger.debug(f"Got frame to write to fifo: {frame}")
        if frame.rate != SAMPLE_RATE:
            logger.warning(
                f"Expected framerate of {SAMPLE_RATE}, got {frame}, the write to fifo will probably fail."
            )
        frame.pts = self.__fifo.samples_written
        logger.debug(f"Writing audio to fifo: {frame}")
        self.__fifo.write(frame)
        self.__sent.clear()
        logger.debug(f"Audio written, example: {frame}")


class ResponsePlayer:
    """When audio is set, it is sent over the track."""

    def __init__(self, send_status: Callable[str, None]):
        self.__sent = asyncio.Event()  # set when the track plays all audio
        self.__track = ResponsePlayerStream(self.__sent)
        self.__send_status = send_status
        logger.info(f"Initialized player track: {audio.track_str(self.__track)}")

    @property
    def audio(self):
        return self.__track

    async def send_utterance(self, frame: AudioFrame):
        """Flush the audio frame to the track and send it real-time then return.
        It's important that it be realtime because we need to be relatively on time for switching from listening to
        thinking and speaking.
        """
        logger.info("Sending utterance...")
        assert frame.rate == SAMPLE_RATE
        self.__track.write_audio(frame)
        frame_time = audio.get_frame_seconds(frame)
        timeout = frame_time + 5.0
        logger.debug(f"frame_time={frame_time:.3f}, timeout={timeout:.3f}")
        try:
            logger.debug(
                f"Awaiting __sent.wait() event from {audio.track_str(self.__track)} upon clearing fifo..."
            )
            await asyncio.wait_for(
                self.__sent.wait(),
                timeout=timeout,
            )
            logger.debug("Track's fifo is cleared.")
        except asyncio.TimeoutError:
            logger.error(
                f"Timed out waiting for audio to be played, frame_time={frame_time} timeout={timeout}"
            )
            raise
        except MediaStreamError:
            logger.error("MediaStreamError")
            raise
        logger.info("Utterance sent!")
