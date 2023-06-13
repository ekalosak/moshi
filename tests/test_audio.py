import io
import tempfile

import pytest
from av import AudioFifo, AudioFrame

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


def test_audio_frame_to_wav(short_audio_frame):
    _, fp = tempfile.mkstemp(suffix=".wav")
    audio.write_audio_frame_to_wav(short_audio_frame, fp)
    loaded_frame = audio.load_wav_to_buffer(fp).read()
    assert (short_audio_frame.to_ndarray() == loaded_frame.to_ndarray()).all()
