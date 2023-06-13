""" Test that the speech module produces synthesized language in av.AudioFrame format. """
import asyncio
import tempfile

from av import AudioFrame
import pytest

from moshi import audio, gcloud, speech

@pytest.mark.asyncio
@pytest.mark.gcloud
@pytest.mark.parametrize('langcode', ['en_US', 'ja', 'es_MX'])
async def test_get_voice(langcode):
    voice = await speech.get_voice(langcode, 'MALE')
    assert voice is not None
    assert 'Standard' in voice.name, "Use 'Standard' as default or $$$^^^"
    assert 'MALE' in str(voice.ssml_gender), "Failed to get the correct gendered voice"

@pytest.mark.asyncio
@pytest.mark.gcloud
async def test_speech_synthesis():
    await gcloud.authenticate()
    text = "Hello World"
    audio_frame = await speech.synthesize_speech(text, 'en_US')
    assert isinstance(audio_frame, AudioFrame)
    assert .2 < audio.get_(audio_frame) < 1.2

@pytest.mark.asyncio
@pytest.mark.openai
async def test_transcribe(short_audio_frame):
    transcript = await asyncio.wait_for(
        speech.transcribe(short_audio_frame),
        timeout=10.
    )
    assert isinstance(transcript, str)
    assert transcript == "test"

@pytest.mark.asyncio
@pytest.mark.openai
@pytest.mark.gcloud
async def test_complementary_synthesis_and_transcription():
    await gcloud.authenticate()
    _, fp = tempfile.mkstemp(suffix='.wav')
    text = "Hello World"
    bytestring = await speech.synthesize_speech(
        text=text,
        language='en_US'
    )
    assert isinstance(transcript, bytes)
    audio.save_bytes_to_wav_file(fp, bytestring)
    audio_frame = audio.load_wav_to_audio_frame(fp)
    assert isinstance(audio_frame, AudioFrame)
    transcript = await speech.transcribe(audio_frame)
    assert isinstance(transcript, str)
    assert transcript == text
