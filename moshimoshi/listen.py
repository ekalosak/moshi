""" This module abstracts specific speech2text implementations for use in the MoshiMoshi app. """
from enum import Enum
import os

from loguru import logger
import speech_recognition as sr

from moshimoshi import util

rec = sr.Recognizer()
mic = sr.Microphone()


@util.timed
def _get_audio_from_mic() -> sr.audio.AudioData:
    with mic as source:
        audio = rec.listen(source)
        logger.debug(f"Got audio: {audio.sample_rate} Hz, {audio.sample_width} sec")
    return audio


@util.timed
def _transcribe_audio(audio: sr.audio.AudioData) -> str:
    """Transcribe audio (sound waves) into text (natural language)."""
    return rec.recognize_whisper_api(audio)


@util.timed
def dialogue_from_mic() -> str:
    """Get user dialogue from the microphone and transcribe it into text."""
    audio = _get_audio_from_mic()
    transcription = _transcribe_audio(audio)
    return transcription
