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

def _payload_from_messages(messages: list[Message]) -> list[dict[str, str]]:
    """ Convert a list of messages into a payload for the messages arg of openai.ChatCompletion.create() """
    payload = []
    for msg in messages:
        msg_ = {'role': msg.role.value, 'content': msg.content}
        payload.append(msg_)
    return payload

def completion_from_assistant(messages: list[Message], n: int=1, **kwargs) -> str | list[str]:
    """ Get the conversational response from the LLM.
    Args:
        n: if > 1, returns a list of responses.
        kwargs: passed directly to the OpenAI
    Details on args:
        https://platform.openai.com/docs/api-reference/chat/create
    """
    assert n > 0 and isinstance(n, int)
    if n > 5:
        logger.warning(f"Generating many responses at once can be costly: n={n}")
    payload = _payload_from_messages(messages)
    logger.debug(f"payload:\n{pformat(payload)}")
    response = openai.ChatCompletion.create(
        model=MODEL,
        messages=payload,
        n=n,
        **kwargs,
    )
    logger.debug(f"response:\n{pformat(response)}")
    msg_contents = []
    for choice in response.choices:
        if reason := choice['finish_reason'] != "stop":
            logger.warning(f"Got finish_reason: {reason}")
        msg_contents.append(choice.message.content)
    if n == 1:
        assert len(msg_contents) == 1
        return msg_contents[0]
    else:
        return msg_contents
