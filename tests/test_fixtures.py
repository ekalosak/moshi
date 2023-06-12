import asyncio

import pytest

from moshi import audio

@pytest.mark.asyncio
async def test_sink(short_audio_track, Sink):
    """ Test the Sink test class, ensuring that it collects audio from a track in its fifo and is suitable for usage in
    other tests"""
    sink = Sink(short_audio_track)
    await sink.start()
    await asyncio.wait_for(
        sink.stream_ended.wait(),
        timeout = 2.5,  # substantially longer than the short_wav
    )
    await sink.stop()
    frame = sink.fifo.read()
    frame_time = audio.get_frame_seconds(frame)
    assert 1. <= frame_time <= 2., "the test.wav is 1.24 sec iirc"
