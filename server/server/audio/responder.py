""" This module provides the ResponsePlayer class that plays audio responses to the remote client speakers. """
import asyncio
import os
import time

from aiortc import MediaStreamTrack
from aiortc.mediastreams import MediaStreamError
from av import AudioFrame, AudioFifo, AudioResampler
from loguru import logger

from server.audio import util
from server import SAMPLE_RATE, AUDIO_FORMAT, AUDIO_LAYOUT

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
        self.__resampler = AudioResampler(
            format=AUDIO_FORMAT,
            layout=AUDIO_LAYOUT,
            rate=SAMPLE_RATE,
        )

    @logger.catch
    async def recv(self) -> AudioFrame:
        """ Return audio from the fifo if it exists, otherwise return silence. """
        frame = self.__fifo.read(FRAME_SIZE, partial=False)
        if frame is None:
            logger.trace("empty frame")
            self.__fifo.read(partial=True)  # drop any partial fragment
            frame = util.empty_frame(
                length=FRAME_SIZE,
                rate=SAMPLE_RATE,
                format=AUDIO_FORMAT,
                layout=AUDIO_LAYOUT,
                pts=None,
            )
            self.__sent.set()  # frame is none means whatever audio was written is flushed
        else:
            logger.trace("non-empty frame")
        frame.pts = self.__pts
        self.__pts += frame.samples
        await self.__throttle_playback(frame)
        logger.trace(f"returning frame: {frame}")
        logger.trace(f"frame energy: {util.get_frame_energy(frame)}")
        return frame

    @logger.catch
    async def __throttle_playback(self, frame: AudioFrame, max_buf_sec=.1):
        """ Ensure client buffer isn't overfull by sleeping until max_buf_sec before the frame should be played relative
        to the start of the stream. """
        if self.__start_time is None:
            self.__start_time = time.monotonic()
        current_time = time.monotonic()
        frame_start_time = self.__start_time + util.get_frame_start_time(frame)
        delay = frame_start_time - (current_time + max_buf_sec)
        delay = max(0., delay)
        logger.trace(f"Throttling playback, sleeping for delay={delay:.3f} sec")
        await asyncio.sleep(delay)

    @logger.catch
    def write_audio(self, frame: AudioFrame):
        logger.debug(f"Got frame to write to fifo: {frame}")
        frame.pts = self.__fifo.samples_written
        logger.debug(f"Writing audio to fifo: {frame}")
        self.__fifo.write(frame)
        self.__sent.clear()
        logger.debug(f"Audio written, example: {frame}")

    @logger.catch
    def __make_resampler(self):
        return AudioResampler(
            format=AUDIO_FORMAT,
            layout=AUDIO_LAYOUT,
            rate=SAMPLE_RATE,
        )

class ResponsePlayer:
    """ When audio is set, it is sent over the track. """
    def __init__(self):
        self.__sent = asyncio.Event()  # set when the track plays all audio
        self.__track = ResponsePlayerStream(self.__sent)
        logger.info(f"Initialized player track: {util._track_str(self.__track)}")

    @property
    def audio(self):
        return self.__track

    @logger.catch
    async def send_utterance(self, frame: AudioFrame):
        """ Flush the audio frame to the track and send it real-time then return.
        It's important that it be realtime because we need to be relatively on time for switching from listening to
        thinking and speaking.
        """
        logger.info("Sending utterance...")
        self.__track.write_audio(frame)
        frame_time = util.get_frame_seconds(frame)
        timeout = frame_time + 5.
        logger.debug(f'frame_time={frame_time:.3f}, timeout={timeout:.3f}')
        try:
            logger.debug(f"Awaiting __sent.wait() event from {util._track_str(self.__track)} upon clearing fifo...")
            await asyncio.wait_for(
                self.__sent.wait(),
                timeout = timeout,
            )
            logger.debug("Track's fifo is cleared.")
        except asyncio.TimeoutError:
            logger.debug(f"Timed out waiting for audio to be played, frame_time={frame_time} timeout={timeout}")
            raise
        except MediaStreamError:
            logger.error("MediaStreamError")
            raise
        logger.info("Utterance sent!")
