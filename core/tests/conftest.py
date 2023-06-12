from pathlib import Path
from unittest import mock

import pytest
import speech_recognition as sr

from moshi import chat

@pytest.fixture
def chatter():
    return chat.CliChatter()

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

@pytest.fixture
def mock_rec_listen(audio):
    with mock.patch('moshi.listen.rec.listen', lambda _: audio):
        yield

@pytest.fixture
def mock_dialogue_from_mic():
    with mock.patch('moshi.chat.listen.dialogue_from_mic', lambda: "test dialogue_from_mic"):
        yield

@pytest.fixture
def mock_completion_from_assistant():
     with mock.patch('moshi.chat.think.completion_from_assistant', lambda _: "test completion_from_assistant"):
        yield

@pytest.fixture
def mock_say():
    with mock.patch('moshi.chat.speak.say', lambda *a, **k: None):
        yield
