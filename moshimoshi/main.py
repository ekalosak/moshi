""" This module provides an entrypoint for the MoshiMoshi app. """
import os

from loguru import logger

from moshimoshi import core

logger.level("TRANSCRIPT", no=25, color="<y><W><u>")
logger.transcript = lambda x: logger.log('TRANSCRIPT', x)

@logger.catch
def main():
    chatbot = core.Chatter()
    chatbot.run()
