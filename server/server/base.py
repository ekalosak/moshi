""" Base class for Chatters. """
from abc import ABC, abstractmethod
class Chatter:

    @abstractmethod
    async def _get_user_utterance(self):
        """ Get user utterance and store it. """
        ...

    @abstractmethod
    async def _get_assistant_response(self):
        """ From the AI assistant, get a response to the user utterance. """
        ...

    @abstractmethod
    async def _get_assistant_response(self):
        """ From the AI assistant, get a response to the user utterance. """
        ...