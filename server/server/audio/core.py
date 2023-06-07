from abc import abstractmethod, ABC

from aiortc.mediastreams import MediaStreamTrack

class SingleTrack(ABC):
    """ Base class for the UtteranceDetector and ResponsePlayer. """
    def __init__(self):
        self.__track = None
        self.__task = None

    @abstractmethod
    async def start(self):
        """ Start the background task. """
        ...

    async def stop(self):
        """ Cancel the background task and free up the track.
        """
        if self.__task is not None:
            self.__task.cancel()
        self.__task = None
        self.__track = None

    def setTrack(self, track: MediaStreamTrack):
        """ Add a track to the class after initialization. Allows for initialization of the object before receiving a
        WebRTC offer, but can be forgotten by user - causing, in all likelihood, await self.start() to fail.
        Usage:
            xyz = Subclass(config)
            ...  # track created
            await xyz.setTrack(track)
            ...
            await xyz.start()

        Args:
            - track: the MediaStreamTrack to read from / write to.
        """
        if track.kind != 'audio':
            raise ValueError(f"Non-audio tracks not supported, got track: {_track_str(track)}")
        if track.readyState != 'live':
            raise ValueError(f"Non-live tracks not supported, got track: {_track_str(track)}")
        if self.__track is not None:
            raise ValueError(f"Track already set: {_track_str(self.__track)}")
        self.__track = track
