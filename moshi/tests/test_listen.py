from unittest import mock

import pytest
from openai.error import RateLimitError

from moshi import listen

@pytest.mark.usefixtures("mock_rec_listen")
def test_get_audio_from_mic(audio):
    raudio = listen._get_audio_from_mic()
    assert audio == raudio

@mock.patch('moshi.listen.rec.recognize_whisper_api', lambda _: "test")
def test_transcribe_audio(audio):
    transcription = listen._transcribe_audio(audio)
    assert transcription == "test"

@pytest.mark.openai
@pytest.mark.xfail(reason="Rate limits from OpenAI", raises=RateLimitError)
def test_transcribe_audio_opeani(audio):
    transcription = listen._transcribe_audio(audio)
    assert transcription == "test"

@pytest.mark.usefixtures("mock_rec_listen")
def test_dialogue_from_mic():
    assert listen.dialogue_from_mic() == "test"

@pytest.mark.openai
@pytest.mark.usefixtures("mock_rec_listen")
@mock.patch('moshi.listen.rec.recognize_whisper_api', lambda _: "test")
@pytest.mark.xfail(reason="Rate limits from OpenAI", raises=RateLimitError)
def test_dialogue_from_mic_openai():
    assert listen.dialogue_from_mic() == "test"
