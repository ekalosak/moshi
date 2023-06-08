import asyncio

from aiortc.mediastreams import MediaStreamError
import av
from av import AudioFrame, AudioFifo
import pytest

from server.audio import responder, util

@pytest.mark.asyncio
async def test_responder_track(short_audio_frame):
    """ Write audio and ensure that the audio is played, takes aprox expected amount of time, and that the played audio
    contains the expected audio data.
    This test exercises the ResponsePlayerStream, it does not exercise the ResponsePlayer.
    """
    empty_seconds = 1.5  # let the ResponsePlayerStream play <empty_seconds> of silence
    audible_seconds = util.get_frame_seconds(short_audio_frame)
    total_expected_sec = empty_seconds + audible_seconds
    sent = asyncio.Event()
    track = responder.ResponsePlayerStream(sent)
    sink = Sink(track)
    await sink.start()
    await asyncio.sleep(empty_seconds)  # ResponsePlayerStream should write empty_seconds of silence
    track.write_audio(short_audio_frame)
    frame_time = util.get_frame_seconds(short_audio_frame)
    timeout = frame_time + 1.
    await asyncio.wait_for(
        sent.wait(),
        timeout
    )
    await sink.stop()
    frame = sink.fifo.read()
    frame_time = util.get_frame_seconds(frame)
    # the extra on top of total_expected_sec accounts for the default 100ms playback throttle plus some compute time
    assert total_expected_sec <= frame_time <= total_expected_sec + .2
    arr = frame.to_ndarray()
    proportion_speech = (arr != 0).sum() / arr.shape[1]
    expected_proportion_speech = audible_seconds / total_expected_sec
    assert expected_proportion_speech - .1 <= proportion_speech <= expected_proportion_speech

@pytest.mark.asyncio
async def test_responder(short_audio_frame):
    """ Check that the ResponsePlayer writes audio to the Sink when it receives the audio and silence while it waits. """
    empty_seconds = 1.
    audible_seconds = util.get_frame_seconds(short_audio_frame)
    total_seconds = empty_seconds + audible_seconds
    player = responder.ResponsePlayer()
    sink = Sink(player.audio)
    await sink.start()  # starts pulling silence (and audio when available) from player stream
    await asyncio.sleep(empty_seconds)
    await player.send_utterance(short_audio_frame)
    await sink.stop()
    frame = sink.fifo.read()
    frame_time = util.get_frame_seconds(frame)
    assert total_seconds <= frame_time <= total_seconds + .2
