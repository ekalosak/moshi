from pathlib import Path

import pytest
from aiortc.contrib import media
from aiortc import mediastreams

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
def audio_track(utterance_wav_file) -> mediastreams.MediaStreamTrack:
    """ A track that plays an utterance. """
    player = media.MediaPlayer(file=str(utterance_wav_file))
    yield player.audio
    player._stop(player.audio)
