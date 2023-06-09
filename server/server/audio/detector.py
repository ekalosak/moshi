""" This module provides the UtteranceDetector class that detects and extracts natural language utterances from audio
tracks.
"""
import asyncio
from dataclasses import dataclass

from aiortc import MediaStreamTrack
from aiortc.mediastreams import MediaStreamError
from av import AudioFrame, AudioFifo
from loguru import logger

from server.audio import util
from server.audio.util import _track_str

@dataclass
class ListeningConfig:
    ambient_noise_measurement_seconds: float=1.5  # how long to measure ambient noise for the background audio energy
    silence_detection_ignore_spike_seconds: float=0.05  # until silence is broken for this long, it still counts as contiguous silence
    utterance_end_silence_seconds: float=1.5  # must be silent for this long after an utterance for detection to terminate
    utterance_length_min_seconds: float=.8  # must speak for this long before detection can occur
    utterance_start_timeout_seconds: float=8.  # how long to wait for user to start speaking before timing out
    utterance_start_speaking_seconds: float=.5  # how long speaking must occur before non-silence is considered a phrase
    utterance_timeout_seconds: float=20.  # how long overall to wait for detection before timing out

class UtteranceDetector:
    """ An audio media sink that detects utterances.
    """
    def __init__(self, config=ListeningConfig()):
        self.__track = None
        self.__task = None
        self.__config = config
        self.__utterance: AudioFrame | None = None
        self.__utterance_lock = asyncio.Lock()  # used to switch between dumping frames from the track and listening to them
        logger.debug(f"Using config: {self.__config}")

    async def start(self):
        """ Start detecting speech. """
        if self.__track is None:
            raise ValueError("Track not yet set, call `your_audio_listener.setTrack(your_track)` before starting listening.")
        self.__task = asyncio.create_task(
            self.__dump_frames(),
            name=f"Main utterance detection frame dump task from track: {_track_str(self.__track)}"
        )

    async def stop(self):
        """ Cancel the background task and free up the track. """
        if self.__task is not None:
            self.__task.cancel()
        self.__task = None
        self.__track = None

    def setTrack(self, track: MediaStreamTrack):
        """ Add a track to the class after initialization. Allows for initialization of the object before receiving a
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
        if track.kind != 'audio':
            raise ValueError(f"Non-audio tracks not supported, got track: {_track_str(track)}")
        if track.readyState != 'live':
            raise ValueError(f"Non-live tracks not supported, got track: {_track_str(track)}")
        if self.__track is not None:
            raise ValueError(f"Track already set: {_track_str(self.__track)}")
        self.__track = track

    async def __dump_frames(self):
        """ While the detector is not actively listening, e.g. during response and computation, it must dump the audio
        frames from the track to remain 'real-time'. Otherwise those audio frames would back up and we'd be processing
        e.g. synthesized speech feedback. """
        while True:
            try:
                await asyncio.wait_for(
                    self.__dump_frame(),
                    timeout=self.__config.utterance_timeout_seconds
                )
            except asyncio.TimeoutError:
                logger.error(f"Timed out waiting to dump a frame after {self.__config.utterance_timeout_seconds} sec.")
            except MediaStreamError:
                logger.error("MediaStreamError - source track is empty")
                raise

    async def __dump_frame(self):
        """ Dump a single frame. Requires __utterance_lock. """
        async with self.__utterance_lock:
            await self.__track.recv()

    async def get_utterance(self) -> AudioFrame:
        """ Listen to the audio track and clip out an audio frame with an utterance. Sets __utterance. Requires
        __utterance_lock. By awaiting this coroutine, the main frame dump task is interrupted by lock acquisition so the
        track's frames are not dumped but instead are available to __utterance_detected and the coroutines it awaits on
        down. """
        logger.info("Detecting utterance...")
        async with self.__utterance_lock:
            try:
                await asyncio.wait_for(
                    self.__detect_utterance(),
                    self.__config.utterance_timeout_seconds
                )
            except asyncio.TimeoutError as e:
                logger.error(f"Timed out waiting for an utterance to be detected: {e}")
        utterance_time = util.get_frame_seconds(self.__utterance)
        logger.info(f"Detected utterance that is {utterance_time:.3f} sec long")
        return self.__utterance

    async def __detect_utterance(self):
        """ Detect natural language speech from an audio track.
        This method sets the self.__utterance containing the entire utterance with surrounding silence removed.
        Upon detecting and setting the utterance, it alerts those waiting on the utterance via the self.__utterance_detected
        event.
        Raises:
            - aiortc.MediaStreamError if the track finishes before the utterance is detected (usually for
              .wav input)
        """
        background_energy = await self.__measure_background_audio_energy()
        logger.debug(f"Detected background_energy: {background_energy:.5f}")
        logger.debug("Waiting for utterance to start...")
        await asyncio.wait_for(
            self.__utterance_started(background_energy),
            timeout=self.__config.utterance_start_timeout_seconds
        )
        fifo = AudioFifo()
        silence_time_sec = 0.
        silence_broken_time = 0.
        total_utterance_sec = 0.
        while silence_time_sec < self.__config.utterance_end_silence_seconds:
            frame = await self.__track.recv()
            frame.pts = None  # required for fifo.write(), not sending over network so OK
            fifo.write(frame)
            frame_energy = util.get_frame_energy(frame)
            frame_time = util.get_frame_seconds(frame)
            if frame_energy < background_energy:
                silence_time_sec += frame_time
                silence_broken_time = 0.
            else:
                silence_broken_time += frame_time
                if silence_broken_time > self.__config.silence_detection_ignore_spike_seconds:
                    silence_time_sec = 0.
            logger.trace(f"silence_time_sec: {silence_time_sec}")
            total_utterance_sec += frame_time
        logger.debug(f"Utterance stopped after {total_utterance_sec:.3f} seconds")
        self.__utterance: AudioFrame = fifo.read()

    async def __measure_background_audio_energy(self) -> float:
        """ For some small time, measure the ambient noise and return the noise energy level. """
        fifo = AudioFifo()
        time_elapsed_sec = 0.
        while time_elapsed_sec < self.__config.ambient_noise_measurement_seconds:
            frame = await self.__track.recv()
            time_elapsed_sec += util.get_frame_seconds(frame)
            fifo.write(frame)
        ambient_noise_frame: AudioFrame = fifo.read()
        ambient_noise_energy: float = util.get_frame_energy(ambient_noise_frame)
        return ambient_noise_energy

    async def __utterance_started(self, background_energy: float):
        """ Hold off until audio energy is high enough for long enough. """
        # all time is mesured relative to the track's audio frames, not wall clock time.
        sustained_speech_seconds = 0.
        total_waiting_seconds = 0.
        while True:
            frame = await self.__track.recv()
            frame_energy = util.get_frame_energy(frame)
            frame_time = util.get_frame_seconds(frame)
            logger.trace(f"sustained_speech_seconds: {sustained_speech_seconds}")
            logger.trace(f"total_waiting_seconds: {total_waiting_seconds}")
            if frame_energy > background_energy:
                sustained_speech_seconds += frame_time
            else:
                sustained_speech_seconds = 0.
            if sustained_speech_seconds > self.__config.utterance_start_speaking_seconds:
                logger.debug(f"Utterance started after {total_waiting_seconds:.3f} seconds")
                return
            total_waiting_seconds += frame_time
