import asyncio
import signal
import tempfile
import textwrap

import av
from av import AudioFrame, AudioFifo
import openai
from loguru import logger

from moshi.speak import (
    NoVoiceError,
    engine,
    _get_voice_for_language,
    _change_language,
)
from moshi.lang import Language
from server import OPENAI_TRANSCRIPTION_MODEL, TimeoutError
from server.audio import util
from server.base import timeout_handler

engine.setProperty('output_format', 'wav')
logger.debug("speech engine output set to wav")

def _speech_to_wav_file(utterance, fp: str, timeout: int=1):
    """ Raises: TimeoutError """
    engine.save_to_file(utterance, fp)
    logger.debug("speech engine save_to_file enqueued")
    signal.signal(signal.SIGALRM, timeout_handler)
    signal.alarm(timeout)  # timeout must be int
    engine.runAndWait()
    signal.alarm(0)
    logger.debug("engine returned")

def synthesize_language(utterance: str, language: Language = Language.EN_US, timeout=1) -> AudioFrame:
    logger.debug(f"Producing utterance: {textwrap.shorten(utterance, 64)}")
    _change_language(language)
    logger.debug(f"Changed to language: {language}")
    # import os
    # fp = os.path.join(os.getcwd(), "test.wav")
    _, fp = tempfile.mkstemp(suffix='.wav')
    logger.debug("Starting speech synthesis...")
    _speech_to_wav_file(utterance, fp, timeout)
    logger.debug(f"Speech synthesized to {fp}")
    fifo = util.load_wav_to_buffer(fp)
    logger.debug(f"Loaded synth speech to buffer: {fifo}")
    frame = fifo.read()
    logger.debug(f"Resampling {frame}")
    res = util.make_resampler()
    frames = res.resample(frame)
    assert len(frames) == 1
    frame = frames[0]
    logger.debug(f"Returning {frame}")
    return frame

async def transcribe(audio: AudioFrame) -> str:
    _, fp = tempfile.mkstemp(suffix='.wav')
    util.write_audio_frame_to_wav(audio, fp)
    logger.debug(f'Transcribing audio from {fp}')
    with open(fp, 'rb') as f:
        # TODO timeout I suppose
        transcript = await asyncio.to_thread(
            openai.Audio.transcribe,
            OPENAI_TRANSCRIPTION_MODEL,
            f,
        )
    logger.debug(f"transcript={transcript}")
    return transcript['text']
