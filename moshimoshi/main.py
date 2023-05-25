""" This module provides an entrypoint for the MoshiMoshi app. """
import os

from loguru import logger

logger.level("TRANSCRIPT", no=25, color="<y><W><u>")
logger.transcript = lambda x: logger.log('TRANSCRIPT', x)

logger.info('Loading MoshiMoshi...')
from moshimoshi import conversation, text2speech, speech2text

DEBUG = bool(os.getenv("MOSHI_DEBUG", False))

@logger.catch
def main():
    if DEBUG:
        text2speech.say("Start")
    else:
        text2speech.say("Welcome to moshi moshi, please start your conversation when you see 'Listening...'")
    while 1:
        logger.debug("Getting user_dialogue...")
        user_dialogue: str = speech2text.listen()
        logger.debug(f"Got user_dialogue:\n'''\n{user_dialogue}\n'''")
        logger.transcript(f'user:\n{user_dialogue}')
        assert isinstance(user_dialogue, str)
        logger.debug("Getting ai_dialogue...")
        response: conversation.Response = conversation.respond(user_dialogue)
        ai_dialogue: str = response.chat_completion
        language: str = response.language
        logger.debug(f"Got ai_dialogue:\n{ai_dialogue}")
        logger.debug(f"Recognized language: {language}")
        logger.transcript(f'assistant:\n{ai_dialogue}')
        assert isinstance(ai_dialogue, str)
        logger.debug("Saying...")
        text2speech.say(ai_dialogue, language)
        logger.debug("Said!")
        logger.warning("Quitting after one loop for development purposes...")
        # TODO add the user and ai dialogue to the prompt
        break
    logger.info('Done chatting!')
