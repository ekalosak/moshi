""" This module provides various language utilities. """
import contextvars
import textwrap

from google.cloud import translate
from loguru import logger

from moshi.exceptions import SetupError

logger.success("Loaded!")

gtransclient = contextvars.ContextVar("gtransclient")

def _setup_client():
    """Set the gtransclient ContextVar."""
    try:
        gtransclient.get()
        logger.debug("gtransclient already exists")
    except LookupError:
        logger.debug("Creating translation client")
        translate_client = translate.TranslationServiceAsyncClient()
        gtransclient.set(translate_client)
        logger.info("Translation client initialized.")

def get_client():
    _setup_client()
    return gtransclient.get()

async def get_voice(language: str) -> str:
    """Get a valid voice for the language."""
    translate_client = get_client()
    response = await tran


async def detect_language(text: str) -> str:
    """Detects the text's language. Run setup_client first.
    Source:
        - https://cloud.google.com/translate/docs/basic/detecting-language#translate-detect-language-multiple-python
    Raises:
        - SetupError if gtransclient not yet set
    """
    translate_client = get_client()
    logger.debug(f"Detecting language for: {textwrap(text, 64)}")
    result = await translate_client.detect_language(text)
    conf = result['confidence']
    lang = result['language']
    logger.debug(f"Confidence: {conf}")
    logger.info(f"Language: {lang}")
    return lang
