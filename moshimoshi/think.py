""" This module abstracts specific chatbot implementations for use in the ChitChat app. """
import os
import pprint
import textwrap

from loguru import logger
import openai

from moshimoshi.base import Message

logger.success("loaded")

class ParseError(Exception):
    """ Raised when there's an error parsing the chat completion. """
    ...

def completion_from_assistant(messages: list[Message]) -> str:
    """ Get the conversational response from the LLM. """
    payload = [msg.asdict() for msg in messages]
    logger.debug(f"MODEL: {MODEL}")
    logger.debug(f"payload: {payload}")
    response = openai.ChatCompletion.create(
        model=MODEL,
        messages=payload,
    )
    logger.debug(f"response: {response}")
    choice = response.choices[0]
    if reason := choice['finish_reason'] != "stop":
        logger.warning(f"Got finish_reason: {reason}")
    logger.debug(f"choice: {choice}")
    return choice.message.content
