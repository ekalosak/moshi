""" This module abstracts specific speech2text implementations for use in the ChitChat app. """
import os

from loguru import logger
import speech_recognition as sr

LANGUAGE = os.getenv('CHAT_LANGUAGE', 'en-US')
RECOGNIZER = os.getenv('CHAT_RECOGNIZER', 'sphinx')

def listen():
    r = sr.Recognizer()
    with sr.Microphone() as source:
        logger.info("Listening...")
        audio = r.listen(source)
        logger.debug(f"Got audio: {audio.sample_rate} Hz, {audio.sample_width} sec")
    if RECOGNIZER == 'sphinx':
        recognized_audio = r.recognize_sphinx(audio, language=LANGUAGE)
    else:
        raise ValueError(f"Unknown CHAT_RECOGNIZER: {RECOGNIZER}")
    logger.info(f"Heard:\n{recognized_audio}")
    return recognized_audio
