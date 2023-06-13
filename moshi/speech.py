import asyncio
import contextvars
import os
import tempfile
import textwrap

import av
from av import AudioFrame, AudioFifo
from google.cloud import texttospeech
import openai
from loguru import logger

from moshi import audio, gcloud

OPENAI_TRANSCRIPTION_MODEL = os.getenv("OPENAI_TRANSCRIPTION_MODEL", "whisper-1")
logger.info(f"Using transcription model: {OPENAI_TRANSCRIPTION_MODEL}")

gttsclient = contextvars.ContextVar('gttsclient')

logger.success("Loaded!")

def _setup_client() -> None:
    try:
        gttsclient.get()
        logger.debug("Text to speech client already exists.")
    except LookupError as e:
        logger.debug("Creating text to speech client...")
        client = texttospeech.TextToSpeechAsyncClient()
        gttsclient.set(client)
        logger.info("Translation client initialized.")

def get_client() -> 'Client':
    _setup_client()
    return gttsclient.get()

async def get_voice(language: str, gender="FEMALE", model="Standard") -> str:
    """Get a valid voice for the language. Just picks the first match.
    Source:
        - https://cloud.google.com/text-to-speech/pricing for list of valid voice model classes
    """
    client = get_client()
    response = await client.list_voices(language_code=language)
    voices = response.voices
    logger.debug(f"Language {language} has {len(voices)} supported voices.")
    for voice in voices:
        if model in voice.name and gender in str(voice.ssml_gender):
            return voice
    raise ValueError(f"Voice not found for language={language}, gender={gender}, model={model}")

async def _synthesize_speech_bytes(text: str, language: 'Language', voice: 'Voice', rate: int=24000) -> bytes:
    """ Synthesize speech to a bytestring in WAV (PCM_16) format.
    Implemented with texttospeech.googleapis.com;
    """
    synthesis_input = texttospeech.SynthesisInput(text=text)
    audio_config = texttospeech.AudioConfig(
        audio_encoding=texttospeech.AudioEncoding.LINEAR16,
        sample_rate_hertz=rate,
    )
    logger.debug(f"Requesting speech synthesis: synthesis_input={synthesis_input}, voice={voice}, audio_config={audio_config}")
    client = get_client()
    response = await client.synthesize_speech(
        input=synthesis_input,
        voice=voice,
        audio_config=audio_config
    )
    logger.debug(f"Got response from texttospeech.synthesize_speech: {response.audio_content[:32]}")
    return response.audio_content

async def synthesize_speech(text: str, language: 'Language', voice: 'Voice', rate: int=24000) -> AudioFrame:
    audio_bytes = await _synthesize_speech_bytes(text, language, voice, rate)
    return audio.wav_bytes_to_audio_frame(audio_bytes)

async def transcribe(audio_frame: AudioFrame) -> str:
    _, fp = tempfile.mkstemp(suffix='.wav')
    audio.write_audio_frame_to_wav(audio_frame, fp)
    logger.debug(f'Transcribing audio from {fp}')
    with open(fp, 'rb') as f:
        # TODO timeout I suppose, also async openai
        transcript = await asyncio.to_thread(
            openai.Audio.transcribe,
            OPENAI_TRANSCRIPTION_MODEL,
            f,
        )
    logger.debug(f"transcript={transcript}")
    return transcript['text']
