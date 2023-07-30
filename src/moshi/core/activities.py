"""Create initial prompt for a an unstructured conversation."""
from abc import ABC, abstractmethod
import dataclasses
import datetime
from enum import Enum
from typing import Annotated, Literal, Union

from loguru import logger
from pydantic import BaseModel, Field

from .base import Message, Role
from .character import Character
from moshi.utils.storage import firestore_client
from moshi.utils import speech, ctx

@dataclasses.dataclass
class Transcript:
    activity_type: str
    messages: list[Message]
    uid: str  # user id from FBA, required to index transcripts in db
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
    __transcript: Transcript = None
    __cid: str = None
    __character: Character = None

    @abstractmethod
    def _init_messages(self) -> list[Message]:
        """Assemble the prompt."""
        ...

    @property
    def messages(self) -> list[Message]:
        return self.__transcript.messages

    @property
    def voice(self):
        return self.__character.voice

    @property
    def lang(self):
        return self.__character.language


    async def start(self):
        await self.__init_transcript()
        await self.__init_character()        

    async def __init_transcript(self):
        """Create the Firestore artifacts for this conversation."""
        act = Activity(activity_type=self.activity_type.value)
        logger.trace(f"Created activity: {act}")
        self.__transcript = Transcript(
            activity_type=self.activity_type,
            uid=ctx.user.get().uid,
            messages=self._init_messages(),
        )
        logger.trace(f"Created conversation: {self.__transcript}")
        collection_ref = firestore_client.collection("transcripts")
        doc_ref = collection_ref.document()
        self.__cid = doc_ref.id
        with logger.contextualize(cid=self.__cid):
            logger.trace(f"Creating new conversation document in Firebase...")
            result = await doc_ref.set(self.__transcript.asdict())
            logger.trace(f"Created new conversation document!")

    async def __init_character(self):
        """Initialize the character for this conversation."""
        logger.trace(f"Creating character...")
        voice = await speech.get_voice(ctx.profile.get().lang)
        logger.trace(f"Selected voice: {voice}")
        self.__character = Character(voice)
        logger.trace(f"Character created: {self.__character}")


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