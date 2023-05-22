""" This module provides an entrypoint for the ChitChat app. """
from loguru import logger

from chitchat import conversation, text2speech, speech2text

def main():
    logger.info('START')
    while 1:
        logger.debug("Getting user_dialogue...")
        user_dialogue: str = speech2text.listen()
        logger.debug(f"Got user_dialogue:\n{user_dialogue}")
        logger.debug("Getting ai_dialogue...")
        ai_dialogue: str = conversation.respond(user_dialogue)
        logger.debug(f"Got ai_dialogue:\n{ai_dialogue}")
        logger.debug("Saying...")
        speech2text.say(ai_dialogue)
        logger.debug("Said!")
    logger.info('END')
