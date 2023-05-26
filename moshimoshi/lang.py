""" This module provides various language utilities. """
from enum import Enum
import os
import pprint

from loguru import logger
import pyttsx3

from moshimoshi.base import Role, Message
from moshimoshi import think

N_COMPLETIONS = os.getenv("MOSHI_LANGUAGE_DETECT_COMPLETIONS", 3)

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

class LanguageNotFoundError(Exception):
    """ Raised when a language code can't be exctracted from the LLM response. """
    ...

def _get_language_from_utterance(utterance: str) -> Language:
    """ Given an OpenAI chat completion, which won't be a consistent format usually, but usually contains the correct
    answer, get the Language out of it.
    Raises LanguageNotFoundError if it can't find one.
    """
    for lang in Language:
        if lang.value in utterance:
            return lang
    raise LanguageNotFoundError(utterance)

def recognize_language(utterance: str) -> Language:
    """ Get the language code corresponding to the language detected in the utterance.
    Raises LanguageNotFoundError if it can't detect the language.
    """
    all_lang_codes = ", ".join(str(lang.value) for lang in Language)
    modified_utterance = f"What is the language code for this utterance: '{utterance}'?"
    messages = [
        Message(Role.SYS, "Return the language code corresponding to the language used by the user."),
        Message(Role.SYS, f"Valid language codes are: {all_lang_codes}"),
        Message(Role.USR, modified_utterance)
    ]
    logger.trace("\n" + pprint.pformat(messages))
    # TODO max_tokens?
    assistant_utterances = think.completion_from_assistant(
        messages,
        n=N_COMPLETIONS,
        presence_penalty=-2,
        temperature=0.2,
    )
    assert all(isinstance(au, str) for au in assistant_utterances)
    for assistant_utterance in assistant_utterances:
        try:
            return _get_language_from_utterance(assistant_utterance)
        except LanguageNotFoundError as e:
            logger.debug(e)
    raise LanguageNotFoundError("None of the responses contained a language code.")
