""" This module abstracts specific speech2text implementations for use in the MoshiMoshi app. """
from enum import Enum
import os

from loguru import logger
import speech_recognition as sr

from moshimoshi import util

class Recognizer(str, Enum):
    SPHINX = "sphinx"
    WHISPER_API = "whisper-api"

RECOGNIZER = Recognizer(os.getenv("MOSHI_RECOGNIZER", "whisper-api"))
LANGUAGE = os.getenv("MOSHI_LANGUAGE")
if LANGUAGE and RECOGNIZER != Recognizer.SPHINX:
    logger.warning(f"Env var MOSHI_LANGUAGE ignored when MOSHI_RECOGNIZER is not sphinx, got: {LANGUAGE} {RECOGNIZER}")

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
    """ Transcribe audio (sound waves) into text (natural language). """
    if RECOGNIZER == Recognizer.SPHINX:
        return rec.recognize_sphinx(audio, language=LANGUAGE)
    elif RECOGNIZER == Recognizer.WHISPER_API:
        return rec.recognize_whisper_api(audio)
    else:
        raise ValueError(f"Unrecognized MOSHI_RECOGNIZER: {MOSHI_RECOGNIZER}")

@util.timed
def dialogue_from_mic() -> str:
    """ Get user dialogue from the microphone and transcribe it into text. """
    audio = _get_audio_from_mic()
    transcription = _transcribe_audio(audio)
    return transcription
