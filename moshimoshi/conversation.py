""" This module abstracts specific chatbot implementations for use in the ChitChat app. """
from dataclasses import dataclass
import os
import pprint
import textwrap

from loguru import logger
import openai

from moshimoshi.text2speech import LANGUAGES

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
2. Be sure to adhere to the output JSON format. Invalid JSON will be rejected.
3. Be sure to use language codes, one of: 'ar_SA', 'en_IN', 'sv_SE', 'id_ID', 'ro_RO', 'ko_KR', 'en_GB', 'nb_NO', 'zh_HK', 'he_IL', 'el_GR', 'pl_PL', 'it_IT', 'da_DK', 'en_AU', 'sk_SK', 'fi_FI', 'fr_FR', 'nl_BE', 'en_US', 'en_IE', 'de_DE', 'es_MX', 'th_TH', 'pt_BR', 'cs_CZ', 'hu_HU', 'nl_NL', 'es_AR', 'zh_TW', 'tr_TR', 'fr_CA', 'ru_RU', 'zh_CN', 'ja_JP', 'pt_PT', 'en_ZA', 'en-scotland', 'hi_IN', 'es_ES'
4. If none of the languages are correct, respond with an error message.

# Example
## Input
user: Hola, me llamo Juan.
assistant: Hola Juan, me llamo Rosa. ¿Como estas?
user: estoy bien. ¿y tu?

## Output
{
    "response": "Yo estoy bien tambien. ¿De donde eres?",
    "language": "es_MX"
}

# Dialogue:
user: """

class ParseError(Exception):
    """ Raised when there's an error parsing the chat completion. """
    ...

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

def _recognize_language(language: str) -> str:
    for lang in LANGUAGES:
        if lang in language:
            logger.debug(f"Recognized language '{lang}' from completion '{language}'")
            return lang
    raise ValueError(f"Language '{language}' not recognized from languages {LANGUAGES}")

def _parse_completion(raw_chat_completion: str) -> tuple[str, str]:
    """ Parse the chat completion into a language and a cleaned chat. """
    try:
        response, language = raw_chat_completion.split('language')
    except ValueError as e:
        logger.error(e)
        raise ParseError(f"'language' not in chat completion: {raw_chat_completion}")
    language = _recognize_language(language)
    chat_completion = _cleanup(response)
    return language, chat_completion

@dataclass
class Response:
    chat_completion: str
    language: str

def respond(user_dialogue: str) -> Response:
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
    if not choice['finish_reason'] == "stop":
        logger.warning(f"Got finish_reason: {choice['finish_reason']}")
    raw_chat_completion = choice.message.content
    language, chat_completion = _parse_completion(raw_chat_completion)
    return Response(chat_completion=chat_completion, language=language)
