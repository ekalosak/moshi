import asyncio
import itertools
import logging
import os
from pathlib import Path
from typing import Callable

import requests
import av
import pytest
from aiortc import MediaStreamTrack
from aiortc.contrib import media
from aiortc.mediastreams import MediaStreamError
from av import AudioFifo, AudioFrame, AudioResampler
from loguru import logger

from moshi import AUDIO_FORMAT, AUDIO_LAYOUT, SAMPLE_RATE, audio
from moshi.utils import log as util

RESOURCEDIR = Path(__file__).parent / "resources"
logging.getLogger("asyncio").setLevel(logging.CRITICAL)

util.setup_loguru()
class FileTrack(MediaStreamTrack):
    """A track that plays a file, then waits for ever on next recv() - rather
    than hanging up with MediaStreamError."""
    kind = "audio"

    def __init__(self, file: str):
        super().__init__()
        print(file)
        self.file = file
        self.framegen = av.open(str(self.file)).decode()

    async def recv(self) -> AudioFrame:
        try:
            frame = next(self.framegen)
        except StopIteration:
            print("FileTrack: end of file reached, waiting forever...")
            await asyncio.sleep(1e6)
        return frame

@pytest.fixture(autouse=True)
def _print_blank_line():
    print()

@pytest.fixture
def utterance_wav_file() -> Path:
    return RESOURCEDIR / "test_phrase_8sec_spoken_13sec_total.wav"


@pytest.fixture
def short_wav_file() -> Path:
    return RESOURCEDIR / "test_one_word.wav"


@pytest.fixture
def short_audio_frame(short_wav_file) -> AudioFrame:
    """Returns a single frame containing the data from a wav file."""
    fifo = AudioFifo()
    with av.open(str(short_wav_file)) as container:
        for frame in container.decode():
            fifo.write(frame)
    frame = fifo.read()
    frame = AudioResampler(rate=SAMPLE_RATE).resample(frame)[0]
    return frame

@pytest.fixture
def short_audio_track(short_wav_file) -> MediaStreamTrack:
    """A track that plays a short audio file."""
    track = FileTrack(short_wav_file)
    try:
        yield track
    finally:
        track.stop()


@pytest.fixture
def utterance_audio_track(utterance_wav_file) -> MediaStreamTrack:
    """A track that plays an utterance."""
    player = media.MediaPlayer(
        file=str(utterance_wav_file),
    )
    yield player.audio
    player._stop(player.audio)


@pytest.fixture
def silent_audio_track() -> MediaStreamTrack:
    class SilentTrack(MediaStreamTrack):
        kind = "audio"
        _pts = 0
        _fl = 1024
        _slp = float(_fl) / SAMPLE_RATE

        async def recv(self) -> AudioFrame:
            frame = audio.empty_frame(
                length=self._fl,
                rate=SAMPLE_RATE,
                format=AUDIO_FORMAT,
                layout=AUDIO_LAYOUT,
                pts=self._pts,
            )
            self._pts += self._fl
            await asyncio.sleep(self._slp)
            return frame

    return SilentTrack()


@pytest.fixture
def Sink() -> "Sink":
    class Sink:
        """When provided with a track, the sink will consume from it into a fifo buffer."""

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
                logger.debug("Sink started")

        async def stop(self):
            self.__task.cancel(f"{self.__class__.__name__}.stop() called")
            self.__task = None

        @logger.catch
        async def _mainloop(self):
            self.stream_ended.clear()
            print("Starting mainloop")
            while 1:
                try:
                    frame = await asyncio.wait_for(self.__track.recv(), timeout=5)
                except MediaStreamError:
                    print("MediaStreamError")
                    break
                self.fifo.write(frame)  # this is the sink
            print("Ending mainloop")
            self.stream_ended.set()

    return Sink


@pytest.fixture
def status_fn() -> Callable[str, None]:
    fn = lambda x: print(f"Status: {x}")
    return fn


"""These fixtures are for testing the auth middleware."""""
@pytest.fixture
def email():
    return "test@test.test"

@pytest.fixture
def password():
    return "testtest"

@pytest.fixture
def url():
    """emulator auth service url"""
    return "http://localhost:9099/identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key=dne"

@pytest.fixture
def auth_token(email, password, url):
    data = {
        "email": email,
        "password": password,
        "returnSecureToken": True
    }
    response = requests.post(url, json=data)
    assert response.status_code == 200, "Add test user to authorized_users collection in Firestore."
    return response.json()["idToken"]