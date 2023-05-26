""" This module provides an entrypoint for the MoshiMoshi app. """
from loguru import logger

from moshimoshi import chat

logger.info("Loading MoshiMoshi...")
logger.debug('creating chatbot...')
chatbot = chat.Chatter()
logger.debug(f"chatbot: {chatbot}")
logger.success("MoshiMoshi loaded!")
logger.info("Starting MoshiMoshi...")
chatbot.run()
logger.success("Goodbye!")
