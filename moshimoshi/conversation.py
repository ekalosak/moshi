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
# Task summary
This dialogue is intended to help the human participant learn a language through conversation. Respond to the
conversation as if you were having a normal chat at a bar or across a table from your partner. Pay special attention to
the human participant's skill with the language and tailor your responses to that level of skill.

# Constraints
1. Be sure to only reply with one response at a time; do not include additional user or ai responses beyond your first.

# Example
## Input
user: Hola, me llamo Juan.
ai: Hola Juan, me llamo Rosa. ¿Como estas?
user: estoy bien. ¿y tu?

## Output
assistant: Yo estoy bien tambien. ¿De donde eres?

# Dialogue:
user: """

def _cleanup(chat_completion: str) -> str:
    """ Remove prompt artifacts from the response. """
    logger.debug('Cleaning the AI response...')
    if chat_completion.startswith('ai: '):
        chat_completion = chat_completion.split('ai: ')[1]
    if 'user: ' in chat_completion:
        chat_completion = chat_completion.split('user: ')[0]
    chat_completion.replace('\n', '')
    logger.debug('AI response cleaned!')
    return chat_completion

def respond(user_dialogue: str) -> str:
    """ Use the AI language model to create a conversational response to the user dialogue. """
    content = PROMPT + user_dialogue + '\nai: '
    message = {
        "role": "user",
        "content": content,
    }
    logger.debug(f"Requesting chat_completion from {MODEL} for message:\n{pprint.pformat(message)}")
    response = openai.ChatCompletion.create(
        model=MODEL,
        messages=[message],
    )
    logger.debug(f"Got response:\n{pprint.pformat(response)}")
    choice = response.choices[0]
    logger.debug(f"Using first choice:\n{pprint.pformat(choice)}")
    raw_chat_completion = choice.message.content
    chat_completion = _cleanup(raw_chat_completion)
    return chat_completion
