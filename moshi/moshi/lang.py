""" This module provides various language utilities. """
import os
import pprint
from enum import Enum

import pyttsx3
from loguru import logger

from moshi import think, Message, Role, Model

N_COMPLETIONS = os.getenv("MOSHI_LANGUAGE_DETECT_COMPLETIONS", 1)
LANGUAGE_DETECT_MODEL = Model(os.getenv("MOSHI_LANGUAGE_DETECT_MODEL", "text-davinci-002"))
logger.info(f"Using N_COMPLETIONS={N_COMPLETIONS} for language detection with LANGUAGE_DETECT_MODEL={LANGUAGE_DETECT_MODEL}")

logger.debug('Loading speech engine...')
engine = pyttsx3.init()

def _language_dict() -> dict[str, str]:
    langd = {}
    for voice in engine.getProperty("voices"):
        for lang in voice.languages:
            langd[lang.replace("-", "_").upper()] = lang
    return langd

logger.debug("Determining supported speech languages...")
Language = Enum("Language", _language_dict())
Language.__eq__ = lambda x, y: x.value[:2] == y.value[:2]
logger.info(f"Supported languages: {set(lang.value[:2] for lang in Language)}")
logger.trace(Language.__members__)

logger.success("loaded")


class LanguageNotFoundError(Exception):
    """Raised when a language code can't be exctracted from the LLM response."""

    ...


def _get_language_from_utterance(utterance: str) -> Language:
    """Given an OpenAI chat completion, which won't be a consistent format usually, but usually contains the correct
    answer, get the Language out of it.
    Raises LanguageNotFoundError if it can't find one.
    """
    for lang in Language:
        if lang.value in utterance:
            return lang
    raise LanguageNotFoundError(utterance)


def recognize_language(utterance: str) -> Language:
    """Get the language code corresponding to the language detected in the utterance.
    Raises LanguageNotFoundError if it can't detect the language.
    """
    assert isinstance(utterance, str)
    all_lang_codes = ", ".join(str(lang.value) for lang in Language)
    modified_utterance = f"What is the language code for this utterance: '{utterance}'?"
    messages = [
        Message(
            Role.SYS,
            "Return the language code corresponding to the language used by the user.",
        ),
        Message(Role.SYS, f"Valid language codes are: {all_lang_codes}"),
        Message(Role.USR, modified_utterance),
    ]
    logger.trace("\n" + pprint.pformat(messages))
    assistant_utterances = think.completion_from_assistant(
        messages,
        n=N_COMPLETIONS,
        max_tokens=16,
        presence_penalty=-2,
        temperature=0.2,
        model=LANGUAGE_DETECT_MODEL,
    )
    if N_COMPLETIONS == 1:
        assistant_utterances = [assistant_utterances]
    assert isinstance(assistant_utterances, list)
    assert all(isinstance(au, str) for au in assistant_utterances)
    for assistant_utterance in assistant_utterances:
        try:
            return _get_language_from_utterance(assistant_utterance)
        except LanguageNotFoundError as e:
            logger.debug(f"Failed to get a language from assistant_utterance: {assistant_utterance}")
            logger.error(str(e))
    raise LanguageNotFoundError("None of the responses contained a language code.")
