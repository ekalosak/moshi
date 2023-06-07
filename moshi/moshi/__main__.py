""" This module provides an entrypoint for the MoshiMoshi app. """
from loguru import logger

from moshi import chat

logger.info("Loading MoshiMoshi...")
logger.debug("creating chatbot...")
chatbot = chat.CliChatter()
logger.debug(f"chatbot: {chatbot}")
logger.success("MoshiMoshi loaded!")
logger.info("Starting MoshiMoshi...")
chatbot.run()
logger.success("Goodbye!")
