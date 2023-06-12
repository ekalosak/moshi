import os

from loguru import logger

from .base import Message, Model, ModelType, Role
from .chat import WebRTCChatter
from .detector import UtteranceDetector
from .responder import ResponsePlayer

# Audio
SAMPLE_RATE = int(os.getenv("MOSHISAMPLERATE", 48000))
AUDIO_FORMAT = os.getenv("MOSHIAUDIOFORMAT", 's16')
AUDIO_LAYOUT = os.getenv("MOSHIAUDIOLAYOUT", 'stereo')
FRAME_SIZE = int(os.getenv("MOSHIFRAMESIZE", 960))
assert FRAME_SIZE >= 128 and FRAME_SIZE <= 4096
logger.info(f"Using sample rate: {SAMPLE_RATE}")
logger.info(f"Using audio format: {AUDIO_FORMAT}")
logger.info(f"Using audio layout: {AUDIO_LAYOUT}")
logger.info(f"Using transport frame size: {FRAME_SIZE}")

# Cloud
GOOGLE_PROJECT = "moshi-001"
logger.info(f"Using Google Cloud project: {GOOGLE_PROJECT}")

# Mainloop
MAX_LOOPS = int(os.getenv('MOSHIMAXLOOPS', 10))
assert MAX_LOOPS >= 0
logger.info(f"Running main loop max times: {MAX_LOOPS}")

# Models
OPENAI_TRANSCRIPTION_MODEL = os.getenv("OPENAI_TRANSCRIPTION_MODEL", "whisper-1")
OPENAI_COMPLETION_MODEL = Model(os.getenv("OPENAI_COMPLETION_MODEL", "text-davinci-002"))
logger.info(f"Using transcription model: {OPENAI_TRANSCRIPTION_MODEL}")
logger.info(f"Using completion model: {OPENAI_COMPLETION_MODEL}")

logger.success("Loaded!")
