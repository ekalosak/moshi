""" This module provides an entrypoint for the MoshiMoshi app. """
from loguru import logger

from moshimoshi import conversation, text2speech, speech2text

logger.level("TRANSCRIPT", no=25, color="<k><W><u>")
logger.transcript = lambda x: logger.log('TRANSCRIPT', x)

@logger.catch
def main():
    logger.info('Starting MoshiMoshi...')
    text2speech.say("Welcome to moshi moshi, please start your conversation.")
    while 1:
        logger.debug("Getting user_dialogue...")
        user_dialogue: str = speech2text.listen()
        logger.debug(f"Got user_dialogue:\n'''\n{user_dialogue}\n'''")
        logger.transcript(f'user:\n{user_dialogue}')
        assert isinstance(user_dialogue, str)
        logger.debug("Getting ai_dialogue...")
        ai_dialogue: str = conversation.respond(user_dialogue)
        logger.debug(f"Got ai_dialogue:\n{ai_dialogue}")
        logger.transcript(f'ai:\n{ai_dialogue}')
        assert isinstance(ai_dialogue, str)
        logger.debug("Saying...")
        text2speech.say(ai_dialogue)
        logger.debug("Said!")
        logger.warning("Quitting after one loop for development purposes...")
        break
    logger.info('Done chatting!')
