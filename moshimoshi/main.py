""" This module provides an entrypoint for the ChitChat app. """
from loguru import logger

from moshimoshi import conversation, text2speech, speech2text

@logger.catch
def main():
    logger.info('Starting MoshiMoshi...')
    while 1:
        logger.debug("Getting user_dialogue...")
        # user_dialogue: str = speech2text.listen()
        user_dialogue = "Hello, my name is Eric."
        logger.warning("Using fixed user_dialogue rather than microphone capture for development purposes.")
        logger.debug(f"Got user_dialogue:\n'''\n{user_dialogue}\n'''")
        assert isinstance(user_dialogue, str)
        logger.debug("Getting ai_dialogue...")
        import sys; sys.exit()
        ai_dialogue: str = conversation.respond(user_dialogue)
        logger.debug(f"Got ai_dialogue:\n{ai_dialogue}")
        assert isinstance(ai_dialogue, str)
        logger.debug("Saying...")
        speech2text.say(ai_dialogue)
        logger.debug("Said!")
        logger.warning("Quitting after one loop for development purposes...")
        break
    logger.info('Done chatting!')
