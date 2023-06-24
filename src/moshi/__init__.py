__version__ = "23.6.24"

import os

from loguru import logger

from .exceptions import UserAuthenticationError, UserResetError
from .base import Message, Model, ModelType, Role
from .gcloud import GOOGLE_PROJECT
from .audio import AUDIO_FORMAT, AUDIO_LAYOUT, SAMPLE_RATE
from .speech import OPENAI_TRANSCRIPTION_MODEL
from .think import OPENAI_COMPLETION_MODEL
from .core import WebRTCChatter

logger.success("Loaded!")
