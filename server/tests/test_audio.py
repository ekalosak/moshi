from av import AudioFrame
import pytest

from server import audio

@pytest.mark.asyncio
@pytest.mark.slow
async def test_audio_listener(audio_track):
    """ Test that the UtteranceDetector can detect an utterance of speech in an audio track containing speech. """
    ud = audio.UtteranceDetector()
    ud.setTrack(audio_track)
    await ud.start()
    # TODO timeout by audio_track._track_audio_len_seconds
    utterance = await ud.get_utterance()
    await ud.stop()
    assert isinstance(utterance, AudioFrame)
    utterance_time = audio.get_frame_seconds(utterance)
    assert 7. <= utterance_time <= 8., f"{str(audio_track)} is about 7.5 seconds of speech"
