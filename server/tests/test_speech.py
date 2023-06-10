""" Test that the speech module produces synthesized language in av.AudioFrame format. """
from av import AudioFrame

from server.audio.util import get_frame_seconds
from server import speech

def test_speech_synthesis():
    frame = speech.synthesize_language("Hello, world")
    print(f'frame: {frame}')
    assert isinstance(frame, AudioFrame)
    frame_sec = get_frame_seconds(frame)
    print(f'frame_sec: {frame_sec}')
    assert .5 < frame_sec < 2.5
