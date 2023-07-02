""" This module abstracts specific chatbot implementations for use in the ChitChat app. """
import os
import re
import textwrap
from dataclasses import asdict
from enum import Enum
from pprint import pformat
from typing import NewType

import openai
from loguru import logger

from moshi import Message, Model, ModelType, Role, secrets

OPENAI_COMPLETION_MODEL = Model(
    os.getenv("OPENAI_COMPLETION_MODEL", "text-davinci-002")
)
logger.info(f"Using completion model: {OPENAI_COMPLETION_MODEL}")
OPENAI_APIKEY_SECRET = os.getenv("OPENAI_APIKEY_SECRET", "openai-api-key-001")
logger.info(f"Using API key from: {OPENAI_APIKEY_SECRET}")

logger.success("Loaded!")

async def _setup_api_key():
    openai.api_key = await secrets.get_secret(OPENAI_APIKEY_SECRET)

def _get_type_of_model(model: Model) -> ModelType:
    """Need to know the type of model for endpoint compatibility.
    Source:
        - https://platform.openai.com/docs/models/model-endpoint-compatibility
    """
    if model == Model.GPT35TURBO or model == Model.GPT35TURBO0301:
        return ModelType.CHAT
    else:
        return ModelType.COMP

def _clean_completion(msg: str) -> str:
    """Remove all the formatting the completion model thinks it should give."""
    logger.debug("Cleaning response...")
    # 1. only keep first response, remove its prefix
    pattern = r"(?:\n|^)([A-Za-z]+:)(?:[ \n\t]*)([^\n\t]+)"
    match = re.search(pattern, msg)
    if match:
        first_response = match.group(2)
        logger.debug(f"Regex matched: {first_response}")
        result = first_response
    else:
        logger.debug("Regex did not match.")
        result = msg
    return result

ChatCompletionPayload = NewType("ChatCompletionPayload", list[dict[str, str]])
CompletionPayload = NewType("CompletionPayload", str)


def _chat_completion_payload_from_messages(
    messages: list[Message],
) -> ChatCompletionPayload:
    """Convert a list of messages into a payload for the messages arg of openai.ChatCompletion.acreate()
    Source:
        - https://platform.openai.com/docs/api-reference/chat
    """
    payload = []
    for msg in messages:
        msg_ = {"role": msg.role.value, "content": msg.content}
        payload.append(msg_)
    logger.debug(f"payload:\n{pformat(payload)}")
    return payload


def _completion_payload_from_messages(messages: list[Message]) -> CompletionPayload:
    """Convert a list of message into a payload for the prompt art of openai.Completion.acreate()
    Source:
        - https://platform.openai.com/docs/api-reference/completions/create
    """
    payload = ["INSTRUCTIONS"]
    instructions = 1
    instr = f"{instructions}. You are the 'assistant', the human participant is the 'user'."  # chat_completion has this notion natively
    payload.append(instr)
    sys_done = False
    for msg in messages:
        if msg.role == Role.SYS:
            if sys_done:
                logger.warning(f"System message out of place, skipping:\n{msg}\n{[msg.role for msg in messages]}")
                continue
            instructions += 1
            msgstr = f"{instructions}. {msg.content}"
        else:
            if not sys_done:
                payload.append("CONVERSATION")
            sys_done = True
            msgstr = f"{msg.role}: {msg.content}"
        payload.append(msgstr)
    payload = "\n".join(payload)
    logger.debug(f"payload:\n{pformat(payload)}")
    return payload


async def _chat_completion(
    payload: ChatCompletionPayload, n: int, model: Model, **kwargs
) -> list[str]:
    """Get the message"""
    msg_contents = []
    assert _get_type_of_model(model) == ModelType.CHAT
    response = await openai.ChatCompletion.acreate(
        model=model,
        messages=payload,
        n=n,
        **kwargs,
    )
    logger.debug(f"response:\n{pformat(response)}")
    for choice in response.choices:
        if reason := choice["finish_reason"] != "stop":
            logger.warning(f"Got finish_reason: {reason}")
        if n > 1:
            logger.warning(f"n={n}, using only first completion")
        msg_contents.append(choice.message.content)
        break
    return msg_contents


async def _completion(
    payload: CompletionPayload, n: int, model: Model, **kwargs
) -> list[str]:
    assert _get_type_of_model(model) == ModelType.COMP
    msg_contents = []
    response = await openai.Completion.acreate(
        model=model,
        prompt=payload,
        n=n,
        **kwargs,
    )
    logger.debug(f"response:\n{pformat(response)}")
    for choice in response.choices:
        if reason := choice["finish_reason"] != "stop":
            logger.warning(f"Got finish_reason: {reason}")
        msg = choice.text.strip()
        if n > 1:
            logger.warning(f"n={n}, using only first completion")
        break
    msg = _clean_completion(msg)
    msg_contents.append(msg)
    return msg_contents


async def completion_from_assistant(
    messages: list[Message], n: int = 1, model=Model.TEXTDAVINCI002, **kwargs
) -> list[str]:
    """Get the conversational response from the LLM.
    Args:
        n: how many responses
        kwargs: passed directly to the OpenAI
    Details on args:
        https://platform.openai.com/docs/api-reference/chat/create
    """
    assert n > 0 and isinstance(n, int)
    if n > 1:
        logger.warning(f"Generating many responses at once can be costly: n={n}")
    msg_contents = []
    if _get_type_of_model(model) == ModelType.CHAT:
        payload = _chat_completion_payload_from_messages(messages)
        msg_contents = await _chat_completion(payload, n, model, **kwargs)
    elif _get_type_of_model(model) == ModelType.COMP:
        payload = _completion_payload_from_messages(messages)
        msg_contents = await _completion(payload, n, model, **kwargs)
    else:
        raise TypeError(f"Model not supported: {MODEL}")
    assert isinstance(msg_contents, list)
    assert all(isinstance(mc, str) for mc in msg_contents)
    return msg_contents
