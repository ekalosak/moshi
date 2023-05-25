""" This module abstracts specific speech2text implementations for use in the MoshiMoshi app. """
from enum import Enum
import os

from loguru import logger
import openai
import speech_recognition as sr

class Recognizer(str, Enum):
    SPHINX = "sphinx"
    WHISPER_API = "whisper-api"

RECOGNIZER = Recognizer(os.getenv("MOSHI_RECOGNIZER", "whisper-api"))
LANGUAGE = os.getenv("MOSHI_LANGUAGE")
if LANGUAGE and RECOGNIZER != Recognizer.SPHINX:
    logger.warning(f"Env var MOSHI_LANGUAGE ignored when MOSHI_RECOGNIZER is not sphinx, got: {LANGUAGE} {RECOGNIZER}")

logger.debug("Setting up listener...")
rec = sr.Recognizer()
logger.success("Listener set up!")
logger.debug("Setting up microphone...")
mic = sr.Microphone()
logger.success("Microphone set up!")

def listen() -> str:
    """ Get user dialogue from the microphone and transcribe it into text. """
    logger.debug('START listen')
    with mic as source:
        logger.info("Listening...")
        audio = rec.listen(source)
        logger.debug(f"Got audio: {audio.sample_rate} Hz, {audio.sample_width} sec")
    recognized_audio = _recognize(audio)
    logger.info(f"Heard: {recognized_audio}")
    logger.debug('END listen')
    return recognized_audio


def _recognize(audio: sr.audio.AudioData) -> str:
    logger.debug("START _recognize")
    if RECOGNIZER == Recognizer.SPHINX:
        recognized_audio = rec.recognize_sphinx(audio, language=LANGUAGE)
    elif RECOGNIZER == Recognizer.WHISPER_API:
        recognized_audio = rec.recognize_whisper_api(audio)
    else:
        raise ValueError(f"Unrecognized MOSHI_RECOGNIZER: {MOSHI_RECOGNIZER}")
    logger.debug("END _recognize")
    return recognized_audio
