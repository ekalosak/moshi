import asyncio
from unittest import mock

import pytest
from aiortc.mediastreams import MediaStreamError
from av import AudioFrame

from moshi import audio, detector


@pytest.mark.asyncio
@pytest.mark.slow
async def test_utterance_detector(utterance_audio_track, status_fn):
    """Test that the UtteranceDetector can detect an utterance of speech in an audio track containing speech."""
    connected = asyncio.Event()
    ud = detector.UtteranceDetector(connected, status_fn)
    print("created UtteranceDetector")
    ud.setTrack(utterance_audio_track)
    print("set track, starting...")
    await ud.start()
    connected.set()
    print("started! getting_utterance...")
    utterance = await ud.get_utterance()
    print("got_utterance! stopping...")
    await ud.stop()
    print("stopped!")
    assert isinstance(utterance, AudioFrame)
    utterance_time = audio.get_frame_seconds(utterance)
    assert (
        8.0 <= utterance_time <= 9.0
    ), f"{str(utterance_audio_track)} is nominally 8.56 seconds of speech"


sleeps = [
    pytest.param(1),
    pytest.param(2),
    pytest.param(5, marks=pytest.mark.slow),
    pytest.param(8, marks=pytest.mark.slow),
    pytest.param(11, marks=pytest.mark.slow),
]


@pytest.mark.asyncio
@pytest.mark.parametrize("sleepsec", sleeps)
async def test_disconnect_bug_15(sleepsec, utterance_audio_track, status_fn):
    """Test user (audio) disconnects throughout the detection flow."""
    connected = asyncio.Event()
    ud = detector.UtteranceDetector(connected, status_fn)
    print("created UtteranceDetector")
    ud.setTrack(utterance_audio_track)
    print("set track, starting...")
    await ud.start()
    connected.set()
    print("started! starting getting_utterance task...")
    task = asyncio.create_task(ud.get_utterance())
    print(f"sleeping sec: {sleepsec}")
    await asyncio.sleep(sleepsec)
    utterance_audio_track.stop()
    await asyncio.sleep(0.5)  # to let event loop get to every timeout etc.
    assert task.done(), "MediaStreamError didn't end up cancelling task."
    assert isinstance(task.exception(), MediaStreamError)


@pytest.mark.asyncio
async def test_timeout_bug_15_user_not_start_speaking(silent_audio_track, status_fn):
    """Test timeout while detecting user utterance due to user not starting speaking."""
    connected = asyncio.Event()
    config = detector.ListeningConfig(
        ambient_noise_measurement_seconds=0.1,
        utterance_start_timeout_seconds=0.5,
    )
    ud = detector.UtteranceDetector(connected, status_fn, config)
    print("created UtteranceDetector")
    ud.setTrack(silent_audio_track)
    print("set track, starting...")
    await ud.start()
    connected.set()
    print("started! starting getting_utterance task...")
    with pytest.raises(asyncio.TimeoutError):
        utframe = await ud.get_utterance()


@pytest.mark.asyncio
async def test_timeout_bug_15_user_speak_too_long(utterance_audio_track, status_fn):
    """Test timeout while detecting user utterance due to user being too chatty."""
    connected = asyncio.Event()
    config = detector.ListeningConfig(
        utterance_timeout_seconds=6.0,  # NOTE utterance_audio_track starts at ~2sec, has ~8sec speaking, ~13sec total
    )
    ud = detector.UtteranceDetector(connected, status_fn, config=config)
    print("created UtteranceDetector")
    ud.setTrack(utterance_audio_track)
    print("set track, starting...")
    await ud.start()
    await asyncio.sleep(0.1)
    connected.set()
    print("started! starting getting_utterance task...")
    with pytest.raises(asyncio.TimeoutError):
        utframe = await ud.get_utterance()
