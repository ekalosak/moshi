""" This module provides the ResponsePlayer class that plays audio responses to the remote client speakers. """
from av import AudioFrame
from loguru import logger

from server.audio.core import SingleTrack

class ResponsePlayer(SingleTrack):
    def __init__(self):
        super().__init__()
        self.__response: AudioFrame | None = None

    async def play_response():
        if self.__track is None:
            raise ValueError("Track not yet set, try calling self.setTrack()")
        if self.__response is None:
            raise ValueError("Response not yet set, try calling self.set_response()")

    async def set_response(response: AudioFrame):
        if self.__response is not None:
            raise ValueError("Response already set")
        self.__response = response
