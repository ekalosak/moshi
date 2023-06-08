import pytest

from server.audio import util

@pytest.mark.skip(reason="Not implemented")
def test_ensure_size(short_audio_frame):
    frame = ensure_size(short_audio_frame, short_audio_frame.samples * 2)
    assert frame.samples == short_audio_frame.samples * 2

def test_empty_frame():
    length = 16
    ef = util.empty_frame(length=length, format='s16', layout='mono')
    assert ef.samples == length
    efa = ef.to_ndarray()
    assert (efa == 0).all()
    assert efa.shape == (1, length)
