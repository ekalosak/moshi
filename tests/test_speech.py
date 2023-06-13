""" Test that the speech module produces synthesized language in av.AudioFrame format. """
import asyncio
import tempfile

import pytest
from av import AudioFrame

from moshi import audio, gcloud, lang, speech


@pytest.mark.asyncio
@pytest.mark.gcloud
@pytest.mark.parametrize("langcode", ["en_US", "ja", "es_MX"])
async def test_get_voice(langcode):
    voice = await speech.get_voice(langcode, "MALE")
    assert voice is not None
    assert "Standard" in voice.name, "Use 'Standard' as default or $$$^^^"
    assert "MALE" in str(voice.ssml_gender), "Failed to get the correct gendered voice"


@pytest.mark.asyncio
@pytest.mark.gcloud
async def test_speech_synthesis():
    await gcloud.authenticate()
    text = "Hello World"
    langcode = "en_US"
    voice = await speech.get_voice(langcode, "FEMALE")
    print(f"type(voice): {type(voice)}")
    audio_frame = await speech.synthesize_speech(text, voice)
    assert isinstance(audio_frame, AudioFrame)
    assert 0.2 < audio.get_frame_seconds(audio_frame) < 1.2


@pytest.mark.asyncio
@pytest.mark.openai
async def test_transcribe(short_audio_frame):
    transcript = await asyncio.wait_for(
        speech.transcribe(short_audio_frame), timeout=10.0
    )
    assert isinstance(transcript, str)
    assert transcript == "test"


@pytest.mark.asyncio
@pytest.mark.openai
@pytest.mark.gcloud
async def test_complementary_synthesis_and_transcription():
    await gcloud.authenticate()
    _, fp = tempfile.mkstemp(suffix=".wav")
    text = "Hello World"
    langcode = "en"
    voice = await speech.get_voice(langcode, "MALE")
    audio_frame = await speech.synthesize_speech(
        text=text,
        voice=voice,
    )
    assert isinstance(audio_frame, AudioFrame)
    transcript = await speech.transcribe(audio_frame)
    assert isinstance(transcript, str)
    print(f"transcript={transcript}")
    print(f"text={text}")
    assert lang.similar(transcript, text) > 0.75
