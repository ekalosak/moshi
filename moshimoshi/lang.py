""" This module provides various language utilities. """
from enum import Enum
import pprint

from loguru import logger
import pyttsx3

from moshimoshi.base import Role, Message
from moshimoshi import think

engine = pyttsx3.init()

def _language_dict() -> dict[str, str]:
    langd = {}
    for voice in engine.getProperty('voices'):
        for lang in voice.languages:
            langd[lang.replace("-", "_").upper()] = lang
    return langd

Language = Enum('Language', _language_dict())
logger.info(f"Supported languages: {set(lang.value[:2] for lang in Language)}")
logger.trace(Language.__members__)

logger.success("loaded")

def recognize_language(utterance: str) -> Language:
    """ Get the language code corresponding to the language detected in the utterance. """
    all_lang_codes = ", ".join(str(lang.value) for lang in Language)
    messages = [
        Message(Role.SYS, "Return the language code corresponding to the language used by the user."),
        Message(Role.SYS, f"Valid language codes are: {all_lang_codes}"),
        Message(Role.USR, utterance)
    ]
    logger.trace("\n" + pprint.pformat(messages))
    return think.completion_from_assistant(messages)
