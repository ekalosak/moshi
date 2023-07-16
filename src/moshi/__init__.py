__version__ = "23.7.2"

from .util import setup_loguru
setup_loguru()

import os

from loguru import logger

from .chat.speech import OPENAI_TRANSCRIPTION_MODEL
from .chat.think import OPENAI_COMPLETION_MODEL
from .core.audio import AUDIO_FORMAT, AUDIO_LAYOUT, SAMPLE_RATE
from .core.base import *
from .core.config import GOOGLE_PROJECT
from .core.exceptions import UserAuthenticationError, UserResetError
# from .core import Chatter

logger.success("Loaded!")
