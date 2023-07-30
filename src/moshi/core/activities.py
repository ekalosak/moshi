"""Create initial prompt for a an unstructured conversation."""
from abc import ABC, abstractmethod
import dataclasses
import datetime
from enum import Enum
from typing import Annotated, Literal, Union

from loguru import logger
from pydantic import BaseModel, Field

from .base import Message, Role
from moshi.utils.storage import firestore_client

@dataclasses.dataclass
class Transcript:
    activity_type: str
    messages: list[Message]
    uid: str  # user id from FBA
    timestamp: datetime.datetime = None

    def asdict(self) -> dict:
        return dataclasses.asdict(self)

    def __post_init__(self):
        self.timestamp = self.timestamp or datetime.datetime.now()

class ActivityType(str, Enum):
    UNSTRUCTURED = "unstructured"

class BaseActivity(ABC, BaseModel):
    """An Activity provides a prompt for a conversation and the database wrapper."""
    activity_type: ActivityType
    __transcript = None
    __cid = None

    @abstractmethod
    def _init_messages(self) -> list[Message]:
        """Assemble the prompt."""
        ...

    async def new_conversation(self, uid: str) -> Transcript:
        """Create a new conversation in the database."""
        collection_ref = firestore_client.collection("conversations")
        act = Activity(activity_type=self.activity_type.value)
        logger.trace(f"Created activity: {act}")
        doc_ref = collection_ref.document()
        self.__cid = doc_ref.id
        self.__transcript = Transcript(
            activity_type=self.activity_type,
            uid=uid,
            messages=self._init_messages(),
        )
        logger.trace(f"Created conversation: {self.__transcript}")
        with logger.contextualize(cid=self.__cid):
            logger.trace(f"Creating new conversation document in Firebase...")
            result = await doc_ref.set(self.__transcript.asdict())
            logger.trace(f"Created new conversation document!")
        return self.__transcript

class Unstructured(BaseActivity):
    activity_type: Literal[ActivityType.UNSTRUCTURED] = ActivityType.UNSTRUCTURED
    def _init_messages(self) -> list[Message]:
        messages = [
            Message(
                Role.SYS,
                "You are a conversational partner for helping language learners practice a second language.",
            ),
            Message(
                Role.SYS,
                "DO NOT provide a translation. Respond in the language the user speaks unless asked explicitly for a translation.",
            ),
            Message(
                Role.SYS,
                "In the conversation section, after these instructions, DO NOT break character.",
            ),
        ]
        return messages

Activity = Annotated[Union[Unstructured, Unstructured], Field(discriminator="activity_type")]