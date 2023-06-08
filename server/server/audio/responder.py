""" This module provides the ResponsePlayer class that plays audio responses to the remote client speakers. """

from aiortc import MediaStreamTrack
from av import AudioFrame, AudioFifo
from loguru import logger

from server.audio.util import _track_str

class ResponsePlayerStream(MediaStreamTrack):
    kind = 'audio'
    def __init__(self):
        super().__init__()

class ResponsePlayer:
    """ When audio is set, it is sent over the track. """
    def __init__(self):
        self.__task = None
        self.__track = ResponsePlayerStream()
        self.__fifo = AudioFifo()

    async def start(self):
        if self.__track is None:
            raise ValueError("Track not yet set, call self.setTrack(track) before starting.")
        if self.__task is None:
            self.__task = asyncio.create_task(
                self.__flush_available_audio(),
                name=f"Play a response over track: {_track_str(self.__track)}"
            )

    @property
    def audio(self):
        return self.__track
