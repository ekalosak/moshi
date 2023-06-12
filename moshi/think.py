""" This module abstracts specific chatbot implementations for use in the ChitChat app. """
import os
import textwrap
from dataclasses import asdict
from enum import Enum
from pprint import pformat
from typing import NewType

import openai
from loguru import logger

from moshi import Model, ModelType, Message, COMPLETION_MODEL

logger.success("Loaded!")


def _get_type_of_model(model: Model) -> ModelType:
    """Need to know the type of model for endpoint compatibility.
    Source:
        - https://platform.openai.com/docs/models/model-endpoint-compatibility
    """
    if model == Model.GPT35TURBO or model == Model.GPT35TURBO0301:
        return ModelType.CHAT
    else:
        return ModelType.COMP


ChatCompletionPayload = NewType("ChatCompletionPayload", list[dict[str, str]])
CompletionPayload = NewType("CompletionPayload", str)


def _chat_completion_payload_from_messages(
    messages: list[Message],
) -> ChatCompletionPayload:
    """Convert a list of messages into a payload for the messages arg of openai.ChatCompletion.create()
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
    """Convert a list of message into a payload for the prompt art of openai.Completion.create()
    Source:
        - https://platform.openai.com/docs/api-reference/completions/create
    """
    payload = ""
    for msg in messages:
        msgstr = f"{msg.role}: {msg.content}"
        payload = payload + '\n' + msgstr
    logger.debug(f"payload:\n{pformat(payload)}")
    return payload


# TODO async openai
def _chat_completion(payload: ChatCompletionPayload, n: int, model: Model, **kwargs) -> list[str]:
    """ Get the message """
    msg_contents = []
    assert _get_type_of_model(model) == ModelType.CHAT
    response = openai.ChatCompletion.create(
        model=model,
        messages=payload,
        n=n,
        **kwargs,
    )
    logger.debug(f"response:\n{pformat(response)}")
    for choice in response.choices:
        if reason := choice["finish_reason"] != "stop":
            logger.warning(f"Got finish_reason: {reason}")
        msg_contents.append(choice.message.content)
    return msg_contents

# TODO async openai
def _completion(payload: CompletionPayload, n: int, model: Model, **kwargs) -> list[str]:
    assert _get_type_of_model(model) == ModelType.COMP
    msg_contents = []
    response = openai.Completion.create(
        model=model,
        prompt=payload,
        n=n,
        **kwargs,
    )
    logger.debug(f"response:\n{pformat(response)}")
    for choice in response.choices:
        if reason := choice["finish_reason"] != "stop":
            logger.warning(f"Got finish_reason: {reason}")
        msg_contents.append(choice.text.strip())
    return msg_contents

# TODO async
def completion_from_assistant(
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
    if n > 5:
        logger.warning(f"Generating many responses at once can be costly: n={n}")
    msg_contents = []
    if _get_type_of_model(model) == ModelType.CHAT:
        payload = _chat_completion_payload_from_messages(messages)
        msg_contents = _chat_completion(payload, n, model, **kwargs)
    elif _get_type_of_model(model) == ModelType.COMP:
        payload = _completion_payload_from_messages(messages)
        msg_contents = _completion(payload, n, model, **kwargs)
    else:
        raise TypeError(f"Model not supported: {MODEL}")
    assert isinstance(msg_contents, list)
    assert all(isinstance(mc, str) for mc in msg_contents)
    return msg_contents
