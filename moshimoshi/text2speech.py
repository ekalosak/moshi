""" This module abstracts specific speech2text implementations for use in the MoshiMoshi app. """
import enum
import textwrap

from loguru import logger
import pyttsx3

logger.debug(f"Setting up speech engine...")
engine = pyttsx3.init()
logger.debug(f"pyttsx3 speech engine: {engine}")
logger.success("Speech engine set up!")

def _list_languages() -> set[str]:
    langs = []
    for voice in engine.getProperty('voices'):
        langs.extend(voice.languages)
    return set(langs)

LANGUAGES = _list_languages()

def _change_language(language: str):
    """ Change the engine's voice to one that supports the desired language.
    Args:
        language  : en_US, de_DE, ...
    """
    if language not in LANGUAGES:
        raise ValueError(f"Language not supported: {language}. Must be one of {LANGUAGES}.")
    for voice in engine.getProperty('voices'):
        if language in voice.languages:
            engine.setProperty('voice', voice.id)
            return True

def say(utterance: str, language='en-scotland'):
    """ Convert an utterance of natural language into audio and play the audio. This is a blocking call. """
    logger.info("Speaking...")
    logger.debug(f"Saying: {textwrap.shorten(utterance, 24)}")
    engine.say(utterance)
    logger.debug('\tevent queued...')
    engine.runAndWait()
    logger.debug('Finished saying utterance.')
    logger.info("Spoke.")

class Speaker:
    # TODO so the prompt can be updated.
    ...
