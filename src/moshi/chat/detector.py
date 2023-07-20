""" This module provides the UtteranceDetector class that detects and extracts natural language utterances from audio
tracks.
"""
import asyncio
from dataclasses import dataclass
from typing import Callable

from aiortc import MediaStreamTrack
from aiortc.mediastreams import MediaStreamError
from av import AudioFifo, AudioFrame
from loguru import logger

from moshi.core import audio

logger.success("Loaded!")


@dataclass
class ListeningConfig:
    ambient_noise_measurement_seconds: float = (
        2.3  # how long to measure ambient noise for the background audio energy
    )
    silence_detection_ignore_spike_seconds: float = 0.05  # until silence is broken for this long, it still counts as contiguous silence
    utterance_end_silence_seconds: float = 1.5  # must be silent for this long after an utterance for detection to terminate
    utterance_length_min_seconds: float = (
        0.8  # must speak for this long before detection can occur
    )
    utterance_start_timeout_seconds: float = (
        8.0  # how long to wait for user to start speaking before timing out
    )
    utterance_start_speaking_seconds: float = (
        0.5  # how long speaking must occur before non-silence is considered a phrase
    )
    utterance_timeout_seconds: float = (
        45.0  # how long overall to wait for detection before timing out
    )


class UtteranceDetector:
    """An audio media sink that detects utterances."""

    def __init__(
        self,
        connected_event: asyncio.Event,
        send_status: Callable[str, None],
        config=ListeningConfig(),
    ):
        self.__track = None
        self.__task = None
        self.__send_status = send_status
        self.__config = config
        self.__utterance: AudioFrame | None = None
        self.__utterance_lock = (
            asyncio.Lock()
        )  # used to switch between dumping frames from the track and listening to them
        self.__background_energy = None
        logger.debug(f"Using config: {self.__config}")
        self.__connected = connected_event

    async def start(self):
        """Start detecting speech."""
        if self.__track is None:
            raise ValueError("Track not yet set.")
        self.__task = asyncio.create_task(
            self.__dump_frames(),
            name=f"Main utterance detection frame dump task from track: {audio.track_str(self.__track)}",
        )

    async def stop(self):
        """Cancel the background task and free up the track."""
        if self.__task is None:
            return
        self.__task.cancel(f"{self.__class__.__name__}.stop() called")
        try:
            await self.__task  # this should sleep until the __task is cancelled
        except asyncio.CancelledError as e:
            logger.debug(
                "asyncio.CancelledError indicating the detection task did not crash but was cancelled"
            )
        finally:
            self.__task = None

    def setTrack(self, track: MediaStreamTrack):
        """Add a track to the class after initialization. Allows for initialization of the object before receiving a
        WebRTC offer, but can be forgotten by user - causing, in all likelihood, await self.start() to fail.
        Usage:
            xyz = Subclass(config)
            ...  # track created
            await xyz.setTrack(track)
            ...
            await xyz.start()
        Args:
            - track: the MediaStreamTrack to read from / write to.
        """
        if track.kind != "audio":
            raise ValueError(
                f"Non-audio tracks not supported, got track: {audio.track_str(track)}"
            )
        if track.readyState != "live":
            raise ValueError(
                f"Non-live tracks not supported, got track: {audio.track_str(track)}"
            )
        if self.__track is not None:
            logger.warning(f"Track already set: {audio.track_str(self.__track)}")
        self.__track = track

    async def __dump_frames(self):
        """While the detector is not actively listening, e.g. during response and computation, it must dump the audio
        frames from the track to remain 'real-time'. Otherwise those audio frames would back up and we'd be processing
        e.g. synthesized speech feedback.
        Raises:
            - aiortc.MediaStreamError
            - asyncio.TimeoutError
        """
        logger.debug(
            "Awaiting ICE connection completion and establishment of all datachannels..."
        )
        await self.__connected.wait()
        logger.debug("ICE connection succeeded!")
        while True:
            try:
                await asyncio.wait_for(
                    self.__dump_frame(), timeout=self.__config.utterance_timeout_seconds
                )
            except asyncio.TimeoutError:
                timeout = self.__config.utterance_timeout_seconds
                logger.debug(f"Timed out waiting to dump a frame after {timeout} sec.")
                self.__send_status(
                    f"Sorry, Moshi will only listen for up to {timeout:.2f} sec per utterance.\n\tWe'll try again!"
                )
                await asyncio.sleep(0.3)
                raise

    async def __dump_frame(self):
        """Dump a single frame. Requires __utterance_lock.
        Raises:
            - MediaStreamError
            - ValueError
        """
        async with self.__utterance_lock:
            if self.__track is not None:
                try:
                    await self.__track.recv()
                except MediaStreamError:
                    logger.debug("User audio disconnected while dumping frame.")
                    raise
            else:
                raise ValueError("Track not set!")

    async def get_utterance(self) -> AudioFrame:
        """Listen to the audio track and clip out an audio frame with an utterance. Sets __utterance. Requires
        __utterance_lock. By awaiting this coroutine, the main frame dump task is interrupted by lock acquisition so the
        track's frames are not dumped but instead are available to __utterance_detected and the coroutines it awaits on
        down.
        Raises:
            - aiortc.MediaStreamError
            - asyncio.TimeoutError
        """
        logger.info("Detecting utterance...")
        async with self.__utterance_lock:
            logger.debug("Acquired lock, awaiting __detect_utterance...")
            try:
                await asyncio.wait_for(
                    self.__detect_utterance(), self.__config.utterance_timeout_seconds
                )
            except asyncio.TimeoutError as e:
                logger.debug(f"Timed out waiting for an utterance to be detected")
                raise
            except MediaStreamError:
                logger.debug("User disconnect while detecting utterance.")
                raise
        utterance_time = audio.get_frame_seconds(self.__utterance)
        logger.info(f"Detected utterance that is {utterance_time:.3f} sec long")
        return self.__utterance

    async def __detect_utterance(self):
        """Detect natural language speech from an audio track.
        This method sets the self.__utterance containing the entire utterance with surrounding silence removed.
        Upon detecting and setting the utterance, it alerts those waiting on the utterance via the self.__utterance_detected
        event.
        Raises:
            - aiortc.MediaStreamError (user disconnect, end of track, etc.)
            - asyncio.TimeoutError (user didn't start speaking)
        """
        if self.__background_energy is None:
            logger.debug("Detecting background energy...")
            self.__send_status(
                "Detecting background noise level for "
                f"{self.__config.ambient_noise_measurement_seconds:.2f} seconds"
            )
            self.__background_energy = await self.__measure_background_audio_energy()
            msg = f"Detected background noise level: {self.__background_energy:.2f}"
            logger.debug(msg)
            self.__send_status(msg)
        logger.debug("Waiting for utterance to start...")
        fifo = AudioFifo()
        timeout = self.__config.utterance_start_timeout_seconds
        self.__send_status(
            f"Listening for up to {timeout} sec for you to start speaking..."
        )
        try:
            first_frame = await asyncio.wait_for(
                self.__utterance_started(),
                timeout=timeout,
            )
        except asyncio.TimeoutError:
            logger.debug("Timed out waiting for user to start speaking.")
            self.__send_status(
                f"Timed out waiting for you to start speaking after {timeout} sec."
            )
            raise
        else:
            logger.debug("User started speaking.")
            self.__send_status("Moshi heard you start speaking...")
        first_frame.pts = None
        fifo.write(first_frame)
        silence_time_sec = 0.0
        silence_broken_time = 0.0
        total_utterance_sec = 0.0
        # utterance not over until silence for > config'd end-of-utterance.
        while silence_time_sec < self.__config.utterance_end_silence_seconds:
            try:
                frame = await self.__track.recv()
            except MediaStreamError:
                logger.debug(
                    "User disconnected audio while we are detecting utterance."
                )
                raise
            frame.pts = (
                None  # required for fifo.write(), not sending over network so OK
            )
            fifo.write(frame)
            frame_energy = audio.get_frame_energy(frame)
            frame_time = audio.get_frame_seconds(frame)
            if frame_energy < self.__background_energy:
                silence_time_sec += frame_time
                silence_broken_time = 0.0
            else:
                silence_broken_time += frame_time
                if (
                    silence_broken_time
                    > self.__config.silence_detection_ignore_spike_seconds
                ):
                    silence_time_sec = 0.0
            logger.trace(f"silence_time_sec: {silence_time_sec}")
            total_utterance_sec += frame_time
        logger.debug(f"Utterance stopped after {total_utterance_sec:.3f} seconds")
        self.__send_status("Moshi heard you stop speaking.")
        self.__utterance: AudioFrame = fifo.read()

    async def __measure_background_audio_energy(self) -> float:
        """For some small time, measure the ambient noise and return the noise energy level.
        Raises:
            - aiortc.MediaStreamError
        """
        fifo = AudioFifo()
        time_elapsed_sec = 0.0
        while time_elapsed_sec < self.__config.ambient_noise_measurement_seconds:
            try:
                frame = await self.__track.recv()
            except MediaStreamError:
                logger.debug("User disconnect while measuring background energy.")
                raise
            time_elapsed_sec += audio.get_frame_seconds(frame)
            frame.pts = None  # or the fifo will complain, we aren't scheduling frames from this fifo so pts=None is OK
            fifo.write(frame)
        ambient_noise_frame: AudioFrame = fifo.read()
        ambient_noise_energy: float = audio.get_frame_energy(ambient_noise_frame)
        ambient_noise_energy = max(ambient_noise_energy, 30.0)  # heuristic
        return ambient_noise_energy

    async def __utterance_started(self) -> AudioFrame:
        """Hold off until audio energy is high enough for long enough."""
        # all time is mesured relative to the track's audio frames, not wall clock time.
        assert isinstance(self.__background_energy, float)
        sustained_speech_seconds = 0.0
        total_waiting_seconds = 0.0
        fifo = AudioFifo()
        while True:
            try:
                frame = await self.__track.recv()
            except MediaStreamError:
                logger.debug(
                    "Audio track disconnect while waiting for utterance to start."
                )
                raise
            frame_energy = audio.get_frame_energy(frame)
            frame_time = audio.get_frame_seconds(frame)
            logger.trace(f"sustained_speech_seconds: {sustained_speech_seconds}")
            logger.trace(f"total_waiting_seconds: {total_waiting_seconds}")
            if frame_energy > self.__background_energy:
                sustained_speech_seconds += frame_time
                frame.pts = None
                fifo.write(frame)
            else:
                sustained_speech_seconds = 0.0
                fifo.read()
            if (
                sustained_speech_seconds
                > self.__config.utterance_start_speaking_seconds
            ):
                logger.debug(
                    f"Utterance started after {total_waiting_seconds:.3f} seconds"
                )
                break
            total_waiting_seconds += frame_time
        return fifo.read()