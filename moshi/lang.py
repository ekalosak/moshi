import asyncio
import contextvars
import textwrap

from google.cloud import translate_v2 as translate
from loguru import logger

gtransclient = contextvars.ContextVar("gtransclient")

logger.success("Loaded!")

def _setup_client():
    """Set the gtransclient ContextVar."""
    try:
        gtransclient.get()
        logger.debug("Translation client already exists.")
    except LookupError:
        logger.debug("Creating translation client...")
        client = translate.Client()
        gtransclient.set(client)
        logger.info("Translation client initialized.")

def get_client() -> 'Client':
    _setup_client()
    return gtransclient.get()

async def detect_language(text: str) -> str:
    """Detects the text's language. Run setup_client first.
    Source:
        - https://cloud.google.com/translate/docs/basic/detecting-language#translate-detect-language-multiple-python
    """
    client = get_client()
    logger.debug(f"Detecting language for: {textwrap.shorten(text, 64)}")
    # NOTE using to_thread rather than TranslationAsyncClient because later has much more complicated syntax
    result = await asyncio.to_thread(
        client.detect_language,
        text,
    )
    conf = result['confidence']
    lang = result['language']
    logger.debug(f"Confidence: {conf}")
    logger.info(f"Language: {lang}")
    return lang
