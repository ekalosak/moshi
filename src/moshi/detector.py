""" This module provides the UtteranceDetector class that detects and extracts natural language utterances from audio
tracks.
"""
import asyncio
from dataclasses import dataclass

from aiortc import MediaStreamTrack
from aiortc.mediastreams import MediaStreamError
from av import AudioFifo, AudioFrame
from loguru import logger

from moshi import audio

logger.success("Loaded!")


@dataclass
class ListeningConfig:
    ambient_noise_measurement_seconds: float = (
        1.5  # how long to measure ambient noise for the background audio energy
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
        20.0  # how long overall to wait for detection before timing out
    )


class UtteranceDetector:
    """An audio media sink that detects utterances."""

    def __init__(self, config=ListeningConfig()):
        self.__track = None
        self.__task = None
        self.__config = config
        self.__utterance: AudioFrame | None = None
        self.__utterance_lock = (
            asyncio.Lock()
        )  # used to switch between dumping frames from the track and listening to them
        self.__background_energy = None
        logger.debug(f"Using config: {self.__config}")

    @logger.catch
    async def start(self):
        """Start detecting speech."""
        if self.__track is None:
            raise ValueError(
                "Track not yet set."
            )
        self.__task = asyncio.create_task(
            self.__dump_frames(),
            name=f"Main utterance detection frame dump task from track: {audio.track_str(self.__track)}",
        )

    @logger.catch
    async def stop(self):
        """Cancel the background task and free up the track."""
        if self.__task is None:
            return
        self.__task.cancel()
        try:
            await self.__task  # this should sleep until the __task is cancelled
        except asyncio.CancelledError as e:
            logger.error(e)
        self.__task = None

    @logger.catch
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
            # raise ValueError(f"Track already set: {audio.track_str(self.__track)}")
        self.__track = track

    # @logger.catch
    async def __dump_frames(self):
        """While the detector is not actively listening, e.g. during response and computation, it must dump the audio
        frames from the track to remain 'real-time'. Otherwise those audio frames would back up and we'd be processing
        e.g. synthesized speech feedback."""
        while True:
            try:
                await asyncio.wait_for(
                    self.__dump_frame(), timeout=self.__config.utterance_timeout_seconds
                )
            except asyncio.TimeoutError:
                logger.error(
                    f"Timed out waiting to dump a frame after {self.__config.utterance_timeout_seconds} sec."
                )
            except MediaStreamError:
                logger.error("MediaStreamError")  # NOTE track probably disconnected
                raise

    # @logger.catch
    async def __dump_frame(self):
        """Dump a single frame. Requires __utterance_lock."""
        async with self.__utterance_lock:
            if self.__track is not None:
                try:
                    await self.__track.recv()
                except MediaStreamError as e:
                    logger.error(e)
                    raise
            else:
                raise ValueError("Track not set!")

    @logger.catch
    async def get_utterance(self, listening_callback=None) -> AudioFrame:
        """Listen to the audio track and clip out an audio frame with an utterance. Sets __utterance. Requires
        __utterance_lock. By awaiting this coroutine, the main frame dump task is interrupted by lock acquisition so the
        track's frames are not dumped but instead are available to __utterance_detected and the coroutines it awaits on
        down."""
        logger.info("Detecting utterance...")
        async with self.__utterance_lock:
            try:
                await asyncio.wait_for(
                    self.__detect_utterance(listening_callback), self.__config.utterance_timeout_seconds
                )
            except asyncio.TimeoutError as e:
                logger.error(f"Timed out waiting for an utterance to be detected: {e}")
                raise
        utterance_time = audio.get_frame_seconds(self.__utterance)
        logger.info(f"Detected utterance that is {utterance_time:.3f} sec long")
        return self.__utterance

    @logger.catch
    async def __detect_utterance(self, listening_callback=None):
        """Detect natural language speech from an audio track.
        This method sets the self.__utterance containing the entire utterance with surrounding silence removed.
        Upon detecting and setting the utterance, it alerts those waiting on the utterance via the self.__utterance_detected
        event.
        Raises:
            - aiortc.MediaStreamError if the track finishes before the utterance is detected (usually for
              .wav input)
        """
        if self.__background_energy is None:
            logger.debug("Detecting background energy...")
            if listening_callback:
                listening_callback("Detecting background noise level...")
            self.__background_energy = await self.__measure_background_audio_energy()
            self.__background_energy = 30.
            logger.warning("Using fixed background energy: 30")
        logger.debug(f"Detected background_energy: {self.__background_energy:.5f}")
        logger.debug("Waiting for utterance to start...")
        fifo = AudioFifo()
        listening_callback("Listening...")
        first_frame = await asyncio.wait_for(
            self.__utterance_started(),
            timeout=self.__config.utterance_start_timeout_seconds,
        )
        first_frame.pts = None
        fifo.write(first_frame)
        silence_time_sec = 0.0
        silence_broken_time = 0.0
        total_utterance_sec = 0.0
        while silence_time_sec < self.__config.utterance_end_silence_seconds:
            frame = await self.__track.recv()
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
        self.__utterance: AudioFrame = fifo.read()

    @logger.catch
    async def __measure_background_audio_energy(self) -> float:
        """For some small time, measure the ambient noise and return the noise energy level."""
        fifo = AudioFifo()
        time_elapsed_sec = 0.0
        while time_elapsed_sec < self.__config.ambient_noise_measurement_seconds:
            frame = await self.__track.recv()
            time_elapsed_sec += audio.get_frame_seconds(frame)
            frame.pts = None  # or the fifo will complain, we aren't scheduling frames from this fifo so pts=None is OK
            fifo.write(frame)
        ambient_noise_frame: AudioFrame = fifo.read()
        ambient_noise_energy: float = audio.get_frame_energy(ambient_noise_frame)
        ambient_noise_energy = max(ambient_noise_energy, 30.0)  # heuristic
        return ambient_noise_energy

    @logger.catch
    async def __utterance_started(self) -> AudioFrame:
        """Hold off until audio energy is high enough for long enough."""
        # all time is mesured relative to the track's audio frames, not wall clock time.
        assert isinstance(self.__background_energy, float)
        sustained_speech_seconds = 0.0
        total_waiting_seconds = 0.0
        fifo = AudioFifo()
        while True:
            frame = await self.__track.recv()
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
