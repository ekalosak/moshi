import asyncio
from pathlib import Path

from aiortc.contrib import media
from aiortc import MediaStreamTrack
from aiortc.mediastreams import MediaStreamError
import av
from av import AudioFrame, AudioFifo
import pytest

RESOURCEDIR = Path(__file__).parent / 'resources'

@pytest.fixture(autouse=True)
def _print_blank_line():
    print()

@pytest.fixture
def utterance_wav_file() -> Path:
    return RESOURCEDIR / 'test_phrase_8sec_spoken_13sec_total.wav'

@pytest.fixture
def short_wav_file() -> Path:
    return RESOURCEDIR / 'test_one_word.wav'

@pytest.fixture
def short_audio_frame(short_wav_file) -> AudioFrame:
    """ Returns a single frame containing the data from a wav file. """
    fifo = AudioFifo()
    with av.open(str(short_wav_file)) as container:
        for frame in container.decode():
            fifo.write(frame)
    return fifo.read()

@pytest.fixture
def short_audio_track(short_wav_file) -> MediaStreamTrack:
    """ A track that plays a short audio file. """
    player = media.MediaPlayer(file=str(short_wav_file))
    yield player.audio
    player._stop(player.audio)

@pytest.fixture
def utterance_audio_track(utterance_wav_file) -> MediaStreamTrack:
    """ A track that plays an utterance. """
    player = media.MediaPlayer(
        file=str(utterance_wav_file),
        loop=True,
    )
    yield player.audio
    player._stop(player.audio)

@pytest.fixture
def Sink() -> 'Sink':
    class Sink:
        """ When provided with a track, the sink will consume from it into a fifo buffer. """
        def __init__(self, track):
            self.__track = track
            self.__task = None
            self.fifo = AudioFifo()
            self.stream_ended = asyncio.Event()

        async def start(self):
            if self.__task is None:
                self.__task = asyncio.create_task(
                    self._mainloop(),
                    name="Test Sink class main loop task",
                )

        async def stop(self):
            self.__task.cancel(f"{self.__class__.__name__}.stop() called")
            self.__task = None

        async def _mainloop(self):
            self.stream_ended.clear()
            while True:
                try:
                    frame = await self.__track.recv()
                except MediaStreamError:
                    break
                try:
                    self.fifo.write(frame)  # this is the sink
                except ValueError as e:
                    raise
            self.stream_ended.set()
    return Sink
