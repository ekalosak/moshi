"""
This module provides the UtteranceDetector class that detects and extracts natural language utterances from audio
tracks.
"""
# TODO dynamic energy threshold detection
import asyncio
from dataclasses import dataclass
import time

from av import AudioFrame, AudioFifo
from loguru import logger
import numpy as np

def get_frame_energy(af: AudioFrame) -> float:
    arr = af.to_ndarray()
    energy = np.sqrt(np.mean(np.square(arr)))
    logger.debug(f"frame energy: {energy}")
    return energy

def get_frame_seconds(af: AudioFrame) -> float:
    return af.samples / af.rate

def _track_str(track) -> str:
    return f"{track.kind}:{track.id}"

@dataclass
class ListeningConfig:
    ambient_noise_measurement_seconds: float=.5  # how long to measure ambient noise for the background audio energy
    utterance_end_silence_seconds: float=.25  # must be silent for this long after an utterance for detection to terminate
    utterance_length_min_seconds: float=.3  # must speak for this long before detection can occur
    utterance_start_timeout_seconds: float=8.  # how long to wait for user to start speaking
    utterance_start_speaking_seconds: float=.5  # how long speaking must occur before non-silence is considered a phrase
    utterance_timeout_seconds: float=30.  # how long overall to wait for detection

class UtteranceDetector:
    """ An audio media sink that detects utterances.
    """
    def __init__(self):
        self.__config = ListeningConfig()
        logger.debug(f"Using config: {self.__config}")
        self.__track = None
        self.__task = None
        self.__utterance: AudioFrame | None = None
        self.__utterance_detected: asyncio.Event = asyncio.Event()

    def setTrack(self, track):
        """ Add a track whose audio should be examined for natural language utterances.
        :param track: A :class:`aiortc.MediaStreamTrack`.
        """
        if track.kind != 'audio':
            raise ValueError(f"Non-audio tracks not supported, got track: {_track_str(track)}")
        if self.__track is not None:
            raise ValueError(f"Track already set: {_track_str(self.__track)}")
        self.__track = track

    async def start(self):
        """ Start detecting speech.
        """
        if self.__track is None:
            raise ValueError("Track not yet set, call `your_audio_listener.setTrack(your_track)` before starting listening.")
        self.__task = asyncio.create_task(
            self.__detect_utterance(),
            name=f"Detect utterance from track: {_track_str(self.__track)}"
        )

    async def stop(self):
        """ Stop detecting speech.
        """
        if self.__task is not None:
            self.__task.cancel()
        self.__task = None
        self.__track = None

    async def __detect_utterance(self):
        """ Detect natural language speech from an audio track.
        This method sets the self.__utterance containing the entire utterance with surrounding silence removed.
        Upon detecting and setting the utterance, it alerts those waiting on the utterance via the self.__utterance_detected
        event.
        """
        background_energy = await self.__measure_background_audio_energy()
        logger.info(f"Detected background_energy: {background_energy}")
        logger.info("Waiting for utterance to start...")
        await asyncio.wait_for(
            self.__utterance_started(background_energy),
            timeout=self.__config.utterance_start_timeout_seconds
        )
        logger.info("Utterance started!")
        fifo = AudioFifo()
        silence_time_sec = 0.
        while silence_time_sec < self.__config.utterance_end_silence_seconds:
            frame = await self.__track.recv()
            fifo.write(frame)
            frame_energy = get_frame_energy(frame)
            logger.debug(f"frame_energy: {frame_energy}")
            if frame_energy < background_energy:
                silence_time_sec += get_frame_seconds(frame)
            else:
                silence_time_sec = 0.
            logger.debug(f"silence_time_sec: {silence_time_sec}")
        logger.info(f"Utterance stopped.")
        self.__utterance: AudioFrame = fifo.read()
        self.__utterance_detected.set()

    async def __measure_background_audio_energy(self) -> float:
        """ For some small time, measure the ambient noise and return the noise energy level. """
        fifo = AudioFifo()
        time_elapsed_sec = 0.
        while time_elapsed_sec < self.__config.ambient_noise_measurement_seconds:
            frame = await self.__track.recv()
            time_elapsed_sec += get_frame_seconds(frame)
            fifo.write(frame)
        ambient_noise_frame: AudioFrame = fifo.read()
        ambient_noise_energy: float = get_frame_energy(ambient_noise_frame)
        return ambient_noise_energy

    async def __utterance_started(self, background_energy: float):
        """ Hold off until audio energy is high enough for long enough. """
        # all time is mesured relative to the track's audio frames, not wall clock time.
        sustained_speech_seconds = 0.
        total_waiting_seconds = 0.
        while True:
            frame = await self.__track.recv()
            frame_energy = get_frame_energy(frame)
            frame_time = get_frame_seconds(frame)
            logger.debug(f"sustained_speech_seconds: {sustained_speech_seconds}")
            logger.debug(f"total_waiting_seconds: {total_waiting_seconds}")
            if frame_energy > background_energy:
                sustained_speech_seconds += frame_time
            else:
                sustained_speech_seconds = 0.
            if sustained_speech_seconds > self.__config.utterance_start_speaking_seconds:
                logger.info(f"Utterance started after {total_waiting_seconds} seconds")
                return
            total_waiting_seconds += frame_time

    async def get_utterance(self, timeout_sec: float=15.):
        await asyncio.wait_for(
            self.__utterance_detected.wait(),
            self.__config.utterance_timeout_seconds
        )
        return self.__utterance
