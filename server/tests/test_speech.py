""" Test that the speech module produces synthesized language in av.AudioFrame format. """
from av import AudioFrame
import pytest

from server.audio.util import get_frame_seconds
from server import speech

def test_speech_synthesis():
    frame = speech.synthesize_language("Hello, world")
    print(f'frame: {frame}')
    assert isinstance(frame, AudioFrame)
    frame_sec = get_frame_seconds(frame)
    print(f'frame_sec: {frame_sec}')
    assert .5 < frame_sec < 2.5

@pytest.mark.asyncio
@pytest.mark.openai
async def test_transcribe(short_audio_frame):
    transcript = await speech.transcribe(short_audio_frame)
    assert isinstance(transcript, str)
    assert transcript == "test"
