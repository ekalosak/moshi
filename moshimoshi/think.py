""" This module abstracts specific chatbot implementations for use in the ChitChat app. """
from dataclasses import asdict
from enum import Enum
import os
from pprint import pformat
import textwrap

from loguru import logger
import openai

from moshimoshi.base import Message

class ModelType(str, Enum):
    """ The two model types used by this app.
    Source:
        - https://platform.openai.com/docs/api-reference/models
    """
    COMP = "completion"
    CHAT = "chat_completion"

class Model(str, Enum):
    """ The various models available. """
    GPT35TURBO =  "gpt-3.5-turbo"
    GPT35TURBO0301 =  "gpt-3.5-turbo-0301"
    TEXTDAVINCI003 = "text-davinci-003"
    TEXTDAVINCI002 = "text-davinci-002"
    TEXTCURIE001 = "text-curie-001"
    TEXTBABBAGE001 = "text-babbage-001"
    TEXTADA001 = "text-ada-001"

MODEL = Model(os.getenv('OPENAI_MODEL', "gpt-3.5-turbo"))
logger.info(f"Using model: {MODEL}")

logger.success("loaded")

def _get_type_of_model(model: Model) -> ModelType:
    """ Need to know the type of model for endpoint compatibility.
    Source:
        - https://platform.openai.com/docs/models/model-endpoint-compatibility
    """
    if model == Model.GPT35TURBO or model == Model.GPT35TURBO0301:
        return ModelType.CHAT
    else:
        return ModelType.COMP

ChatCompletionPayload = NewType('ChatCompletionPayload', list[dict[str, str]])
CompletionPayload = NewType('CompletionPayload', str)

def _chat_completion_payload_from_messages(messages: list[Message]) -> ChatCompletionPayload:
    """ Convert a list of messages into a payload for the messages arg of openai.ChatCompletion.create()
    Source:
        - https://platform.openai.com/docs/api-reference/chat
    """
    payload = []
    for msg in messages:
        msg_ = {'role': msg.role.value, 'content': msg.content}
        payload.append(msg_)
    return payload

def _completion_payload_from_messages(messages: list[Message]) -> CompletionPayload:
    """ Convert a list of message into a payload for the prompt art of openai.Completion.create()
    Source:
        - https://platform.openai.com/docs/api-reference/completions/create
    """
    ...

def _chat_completion(payload: ChatCompletionPayload, n: int, **kwargs):
    ...

def _completion(payload: CompletionPayload, n: int, **kwargs):
    ...

# TODO handle InvalidRequestError
# TODO handle RateLimitError
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
    # TODO BELOW: make behavior depend on model type
    payload = _chat_completion_payload_from_messages(messages)
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
