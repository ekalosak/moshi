""" This module wraps the moshi.chatter for use in the WebRTC server. """
import asyncio

from loguru import logger

from server import audio
from moshi import chat

class WebChatter:
    """ This class does two important things:
    1. Coordinates the detector and responder, and
    2. Adapts the moshi.CliChatter for use in the WebRTC server.
    """
    def __init__(self):
        self.__detector = audio.UtteranceDetector()  # get_utterance: track -> AudioFrame
        self.__responder = audio.ResponsePlayer()  # play_response: AudioFrame -> track
        # TODO a lock for coordinating listening and responding

    async def setTrack(self, track):
        await asyncio.gather(
            self.__detector.setTrack(track),
            self.__responder.setTrack(track),
        )

    async def start(self):
        await self.__detector.start()
        await self.__responder.start()

    async def stop(self):
        await asyncio.gather(
            self.__detector.stop(),
            self.__responder.stop(),
        )

    # TODO 
