""" This module provides an entrypoint for the MoshiMoshi app. """
from moshimoshi import core

@logger.catch
def main():
    chatbot = core.Chatter()
    chatbot.run()
