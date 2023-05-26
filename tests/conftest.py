from pathlib import Path

import pytest
import speech_recognition as sr

from moshimoshi import chat

@pytest.fixture
def chatter():
    return chat.Chatter()

@pytest.fixture
def audio_file():
    return Path(__file__).parent / 'resources/test.wav'

@pytest.fixture
def audio(audio_file):
    print(audio_file)
    rec = sr.Recognizer()
    with sr.AudioFile(str(audio_file)) as src:
        audio = rec.record(src)
    return audio
