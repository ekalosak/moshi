import pytest

from server import audio

@pytest.mark.asyncio
async def test_audio_listener(audio_track):
    al = audio.AudioListener()
    al.addTrack(audio_track)
    await al.start()
    # TODO timeout by audio_track._track_audio_len_seconds
    transcript = await al.get_transcript()
    await al.stop()
    assert transcript == audio_track._transcript
