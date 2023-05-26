from unittest import mock

import pytest

from moshimoshi import listen

def test_get_audio_from_mic(audio):
    with mock.patch('moshimoshi.listen.rec.listen', lambda _: audio):
        raudio = listen._get_audio_from_mic()
    assert audio == raudio

@pytest.mark.openai
def test_transcribe_audio(audio):
    transcription = _transcribe_audio(audio)
    assert transcription == "test"

@mock.patch('moshimoshi.listen.rec.recognize_whisper_api', lambda _: "test")
def test_transcribe_audio(audio):
    transcription = _transcribe_audio(audio)
