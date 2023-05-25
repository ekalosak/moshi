""" This module abstracts specific speech2text implementations for use in the MoshiMoshi app. """
import textwrap

from loguru import logger
import pyttsx3  # TODO use whisper tts

logger.debug(f"Setting up speech engine...")
engine = pyttsx3.init()
logger.debug(f"pyttsx3 speech engine: {engine}")
logger.success("Speech engine set up!")

def say(utterance: str):
    """ Convert an utterance of natural language into audio and play the audio. This is a blocking call. """
    logger.info("Speaking...")
    logger.debug(f"Saying: {textwrap.shorten(utterance, 24)}")
    engine.say(utterance)
    logger.debug('\tevent queued...')
    engine.runAndWait()
    logger.debug('Finished saying utterance.')
    logger.info("Spoke.")
