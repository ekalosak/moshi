import os

from server.base import TimeoutError

SAMPLE_RATE = int(os.getenv("MOSHISAMPLERATE", 48000))
AUDIO_FORMAT = os.getenv("MOSHIAUDIOFORMAT", 's16')
AUDIO_LAYOUT = os.getenv("MOSHIAUDIOFORMAT", 'stereo')
OPENAI_TRANSCRIPTION_MODEL = os.getenv("OPENAI_TRANSCRIPTION_MODEL", "whisper-1")
