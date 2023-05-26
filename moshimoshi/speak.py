""" This module abstracts specific speech2text implementations for use in the MoshiMoshi app. """
import textwrap

from loguru import logger
import pyttsx3

from moshimoshi import util
from moshimoshi.lang import Language

engine = pyttsx3.init()

logger.success("loaded")

class NoVoiceError(Exception):
    """ Raised when a voice can't be found for a particular language. """
    ...

def _get_voice_for_language(language: Language) -> pyttsx3.voice.Voice:
    """ Get an appropriate pyttsx3 voice for the language.
    Raises NoVoiceError if no such voice can be found.
    """
    for voice in engine.getProperty('voices'):
        if language.value in voice.languages:
            logger.debug(f"voice: {voice}")
            return voice
    raise NoVoiceError(language)

def _change_language(language: Language):
    """ Change the engine's voice to one that supports the desired language.  """
    voice = _get_voice_for_language(language)
    engine.setProperty('voice', voice.id)

@util.timed
def say(utterance: str, language: Language=Language.EN_US):
    """ Convert an utterance of natural language into audio and play the audio. This is a blocking call. """
    logger.debug(f"utterance: {textwrap.shorten(utterance, 64)}")
    _change_language(language)
    engine.say(utterance)
    engine.runAndWait()
