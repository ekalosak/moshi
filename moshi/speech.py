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

def setup_client() -> None:
    try:
        gttsclient.get()
        logger.debug("Text to speech client already exists.")
    except LookupError as e:
        logger.debug("Creating text to speech client...")
        tts_client = texttospeech.TextToSpeechAsyncClient()
        logger.success("Loaded!")

def get_client() -> 'Client':
    setup_client()
    return gttsclient.get()

async def synthesize_speech(text: str, language: 'Language', rate: int=24000) -> bytes:
    """ Synthesize speech to a bytestring in WAV (PCM_16) format.
    Implemented with texttospeech.googleapis.com;
    """
    synthesis_input = texttospeech.SynthesisInput(text=text)
    voice = texttospeech.VoiceSelectionParams(
        language_code=language,
        ssml_gender=texttospeech.SsmlVoiceGender.NEUTRAL
    )
    audio_config = texttospeech.AudioConfig(
        audio_encoding=texttospeech.AudioEncoding.LINEAR16,
        sample_rate_hertz=rate,
    )
    logger.debug(f"Requesting speech synthesis: synthesis_input={synthesis_input}, voice={voice}, audio_config={audio_config}")
    response = await client.synthesize_speech(
        input=synthesis_input,
        voice=voice,
        audio_config=audio_config
    )
    logger.debug(f"Got response from texttospeech.synthesize_speech: {textwrap.shorten(response, 96)}")
    return response.audio_content


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
