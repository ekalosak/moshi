from pathlib import Path

from aiortc.contrib import media
from aiortc import MediaStreamTrack
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
    player = media.MediaPlayer(file=str(utterance_wav_file))
    yield player.audio
    player._stop(player.audio)
