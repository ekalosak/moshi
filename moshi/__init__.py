import os

from loguru import logger

from .audio import AUDIO_FORMAT, AUDIO_LAYOUT, SAMPLE_RATE
from .base import Message, Model, ModelType, Role
from .core import WebRTCChatter
from .exceptions import AuthenticationError
from .gcloud import GOOGLE_PROJECT
from .speech import OPENAI_TRANSCRIPTION_MODEL
from .think import OPENAI_COMPLETION_MODEL

logger.success("Loaded!")
