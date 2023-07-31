"""Create initial prompt for a an unstructured conversation."""
from abc import ABC, abstractmethod
import asyncio
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

transcript_col = firestore_client.collection("transcripts")
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

    @property
    def cid(self):
        return self.__cid

    def add_msg(self, msg: Message):
        self.__transcript.messages.append(msg)

    async def start(self):
        await asyncio.gather(self.__init_transcript(), self.__init_character())
        logger.success("Activity started!")

    async def stop(self):
        """Save the transcript to Firestore."""
        await self.__save()

    async def __init_transcript(self):
        """Create the Firestore artifacts for this conversation."""
        self.__transcript = Transcript(
            activity_type=self.activity_type,
            uid=ctx.user.get().uid,
            messages=self._init_messages(),
        )
        await self.__save()
        logger.debug(f"Transcript initialized.")

    async def __init_character(self):
        """Initialize the character for this conversation."""
        logger.debug(f"Creating character...")
        lang = ctx.profile.get().lang
        voice = await speech.get_voice(lang)
        logger.debug(f"Selected voice: {voice}")
        self.__character = Character(voice)
        logger.debug(f"Character initialized: {self.__character}")

    async def __save(self):
        """Save the transcript to Firestore."""
        if self.__cid:
            logger.info("Updating existing doc...")
            doc_ref = transcript_col.document(self.__cid)
        else:
            logger.info("Creating new conversation document...")
            doc_ref = transcript_col.document()
            self.__cid = doc_ref.id
        with logger.contextualize(cid=self.__cid):
            logger.debug(f"Saving conversation document...")
            try:
                await doc_ref.set(self.__transcript.asdict())
                logger.success(f"Updated conversation document!")
            except asyncio.CancelledError:
                logger.debug(f"Cancelled saving conversation document.")



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