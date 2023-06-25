import asyncio

import pytest
from av import AudioFrame

from moshi import audio, detector


@pytest.mark.asyncio
@pytest.mark.slow
async def test_utterance_detector(utterance_audio_track):
    """Test that the UtteranceDetector can detect an utterance of speech in an audio track containing speech."""
    connected = asyncio.Event()
    ud = detector.UtteranceDetector(connected)
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
