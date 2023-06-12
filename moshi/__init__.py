import os

from loguru import logger

from .audio import AUDIO_FORMAT, AUDIO_LAYOUT, SAMPLE_RATE
from .base import Message, Model, ModelType, Role
from .core import WebRTCChatter
from .gcloud import GOOGLE_PROJECT
from .detector import UtteranceDetector
from .responder import ResponsePlayer

# Audio
FRAME_SIZE = int(os.getenv("MOSHIFRAMESIZE", 960))
assert FRAME_SIZE >= 128 and FRAME_SIZE <= 4096
logger.info(f"Using transport frame size: {FRAME_SIZE}")

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
