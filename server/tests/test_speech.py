""" Test that the speech module produces synthesized language in av.AudioFrame format. """
import asyncio

from av import AudioFrame
import pytest

from server.audio.util import get_frame_seconds
from server import speech

@pytest.mark.asyncio
async def test_speech_synthesis():
    print('calling speech.synthesize_language...')
    try:
        frame = await asyncio.wait_for(
            speech.synthesize_language("Hello, world"),
            timeout=2.
        )
    except asyncio.TimeoutError:
        print("Sometimes the engine will hang..?")
        raise
    print('speech.synthesize_language returned!')
    print(f'frame: {frame}')
    assert isinstance(frame, AudioFrame)
    frame_sec = get_frame_seconds(frame)
    print(f'frame_sec: {frame_sec}')
    assert .5 < frame_sec < 2.5

@pytest.mark.asyncio
@pytest.mark.openai
async def test_transcribe(short_audio_frame):
    transcript = await asyncio.wait_for(
        speech.transcribe(short_audio_frame),
        timeout=10.
    )
    assert isinstance(transcript, str)
    assert transcript == "test"
