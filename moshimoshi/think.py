""" This module abstracts specific chatbot implementations for use in the ChitChat app. """
from dataclasses import asdict
import os
from pprint import pformat
import textwrap

from loguru import logger
import openai

from moshimoshi.base import Message

MODEL = os.getenv('OPENAI_MODEL', "gpt-3.5-turbo")
logger.info(f"Using model: {MODEL}")

logger.success("loaded")

def completion_from_assistant(messages: list[Message]) -> str:
    """ Get the conversational response from the LLM. """
    payload = [asdict(msg) for msg in messages]
    logger.debug(f"payload:\n{pformat(payload)}")
    response = openai.ChatCompletion.create(
        model=MODEL,
        messages=payload,
    )
    logger.debug(f"response:\n{pformat(response)}")
    choice = response.choices[0]
    if reason := choice['finish_reason'] != "stop":
        logger.warning(f"Got finish_reason: {reason}")
    logger.debug(f"choice: {choice}")
    return choice.message.content
