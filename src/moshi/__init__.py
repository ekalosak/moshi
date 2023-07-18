__version__ = "23.7.2"

import os

from loguru import logger

from .core.exceptions import UserAuthenticationError, UserResetError
from .core.base import Message, Model, ModelType, Role
from .core.gcloud import GOOGLE_PROJECT
from .core.audio import AUDIO_FORMAT, AUDIO_LAYOUT, SAMPLE_RATE

logger.success("Loaded!")
