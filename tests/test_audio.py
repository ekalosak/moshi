import tempfile

import pytest
from av import AudioFrame
import numpy as np

from moshi import audio


def test_empty_frame():
    length = 16
    ef = audio.empty_frame(length=length, format="s16", layout="mono")
    assert ef.samples == length
    efa = ef.to_ndarray()
    assert (efa == 0).all()
    assert efa.shape == (1, length)


@pytest.mark.asyncio
async def test_get_frame_start_time(short_audio_track):
    t0 = 0
    for i in range(5):
        frame = await short_audio_track.recv()
        frame_start_time = audio.get_frame_start_time(frame)
        assert t0 == frame_start_time
        t0 += frame.samples / frame.rate


def test_af2wavbytes(short_audio_frame):
    b = audio.af2wavbytes(short_audio_frame)
    bn = np.frombuffer(b, dtype=np.int16)
    af = AudioFrame.from_ndarray(
        np.atleast_2d(bn),
        format=short_audio_frame.format.name,
        layout=short_audio_frame.layout.name,
    )
    assert (short_audio_frame.to_ndarray() == af.to_ndarray()).all()

def test_wavbytes2af(short_audio_frame):
    """Test that af2wavbytes and wavbytes2af are inverses."""
    b = audio.af2wavbytes(short_audio_frame)
    af = audio.wavbytes2af(b)
    assert (short_audio_frame.to_ndarray() == af.to_ndarray()).all()
    assert af.format.name == short_audio_frame.format.name
    assert af.layout.name == short_audio_frame.layout.name
    assert af.rate == short_audio_frame.rate