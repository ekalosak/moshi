""" This module abstracts specific chatbot implementations for use in the ChitChat app. """
import os
import pprint
import textwrap

from loguru import logger
import openai

logger.info("Looking for OpenAI API key...")
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
if OPENAI_API_KEY is None:
    raise ValueError("Missing required environment variable: OPENAI_API_KEY")
openai.api_key = OPENAI_API_KEY
logger.success("OpenAI API key found!")

logger.info("Getting OpenAI models...")
MODEL = os.getenv('OPENAI_MODEL', "gpt-3.5-turbo")
_models = [model['id'] for model in openai.Model.list()['data']]
logger.debug(f"Got OpenAI model list: {textwrap.shorten(str(_models), 96)}")
if MODEL not in _models:
    raise ValueError(f"Invalid OPENAI_MODEL: {MODEL}\nMust be one of: {_models}")
logger.success(f"Using OpenAI model: {MODEL}")

PROMPT = """
This dialogue is intended to help the human participant learn a language through conversation. Respond to the
conversation as if you were having a normal chat at a bar or across a table from your partner. Pay special attention to
the human participant's skill with the language and tailor your responses to that level of skill.

Example input:
user: Hola, me llamo Juan.

Expected output:
assistant: Hola Juan, me llamo Rosa. ¿Como estas?
"""

def respond(user_dialogue: str) -> str:
    """ Use the AI language model to create a conversational response to the user dialogue. """
    content = PROMPT + user_dialogue
    message = {
        "role": "user",
        "content": content,
    }
    logger.debug(f"Requesting chat_completion from {MODEL} for message:\n{pprint.pformat(message)}")
    chat_completion = openai.ChatCompletion.create(
        model=MODEL,
        messages=[message],
    )
    logger.debug(f"Got chat_completion:\n{pprint.pformat(chat_completion)}")
    return chat_completion
