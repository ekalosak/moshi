import pytest
import speech_recognition as sr

@pytest.fixture
def audio_pair():
    audio: sr.audio.AudioData
    expected_result: str
