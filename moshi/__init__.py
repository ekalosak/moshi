import os
from .base import Message, Model, ModelType, Role
from .chat import WebRTCChatter
from .detector import UtteranceDetector
from .responder import ResponsePlayer

# Audio
SAMPLE_RATE = int(os.getenv("MOSHISAMPLERATE", 48000))
AUDIO_FORMAT = os.getenv("MOSHIAUDIOFORMAT", 's16')
AUDIO_LAYOUT = os.getenv("MOSHIAUDIOFORMAT", 'stereo')

# Cloud
GOOGLE_PROJECT = "moshi-001"

# Mainloop
MAX_LOOPS = int(os.getenv('MOSHIMAXLOOPS', 10))
assert MAX_LOOPS >= 0

# Models
OPENAI_TRANSCRIPTION_MODEL = os.getenv("OPENAI_TRANSCRIPTION_MODEL", "whisper-1")
