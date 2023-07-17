""" Base types. """
import dataclasses
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
# from uuid import uuid4

from loguru import logger

logger.success("Loaded!")


class Role(str, Enum):
    SYS = "system"
    USR = "user"
    AST = "assistant"

@dataclass
class Message:
    # NOTE .asdict()
    role: Role
    content: str

@dataclass
class Conversation:
    kind: str
    messages: list[Message]
    uid: str  # user id from FB
    timestamp: datetime = None

    def asdict(self) -> dict:
        return dataclasses.asdict(self)

    def __post_init__(self):
        self.timestamp = self.timestamp or datetime.now()

# TODO Model(ABC, str, Enum), ChatModel(Model), CompletionModel(Model)
class ModelType(str, Enum):
    """The two model types used by this app.
    Source:
        - https://platform.openai.com/docs/api-reference/models
    """

    COMP = "completion"
    CHAT = "chat_completion"


class Model(str, Enum):
    """The various models available."""

    GPT35TURBO = "gpt-3.5-turbo"
    GPT35TURBO0301 = "gpt-3.5-turbo-0301"
    TEXTDAVINCI003 = "text-davinci-003"
    TEXTDAVINCI002 = "text-davinci-002"
    TEXTCURIE001 = "text-curie-001"
    TEXTBABBAGE001 = "text-babbage-001"
    TEXTADA001 = "text-ada-001"
