import asyncio
import tempfile
import textwrap

import av
from av import AudioFrame, AudioFifo
from loguru import logger

from moshi.speak import (
    NoVoiceError,
    engine,
    _get_voice_for_language,
    _change_language,
)
from moshi.lang import Language

def _speech_to_wav_file(utterance, fp: str):
    engine.setProperty('output_format', 'wav')
    engine.save_to_file(utterance, fp)
    engine.runAndWait()

def _load_wav_to_buffer(fp: str) -> AudioFifo:
    try:
        container = av.open(fp, 'r')
        fifo = AudioFifo()
        for frame in container.decode(audio=0):
            fifo.write(frame)
    finally:
        container.close()
    return fifo

def say(utterance: str, language: Language = Language.EN_US) -> AudioFrame:
    logger.debug(f"Producing utterance: {textwrap.shorten(utterance, 64)}")
    _change_language(language)
    # import os
    # fp = os.path.join(os.getcwd(), "test.wav")
    _, fp = tempfile.mkstemp(suffix='.wav')
    logger.debug("Starting speech synthesis...")
    _speech_to_wav_file(utterance, fp)
    logger.debug(f"Speech synthesized to {fp}")
    fifo = _load_wav_to_buffer(fp)
    logger.debug(f"Loaded synth speech to buffer: {fifo}")
    frame = fifo.read()
    logger.debug(f"Returning {frame}")
    return frame
