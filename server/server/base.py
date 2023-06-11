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


class TimeoutError(Exception):
    ...

def timeout_handler(signum, frame):
    print(f"signum={signum}")
    print(f"frame={frame}")
    raise TimeoutError("Function timed out!")
