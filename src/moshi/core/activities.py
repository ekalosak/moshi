"""Create initial prompt for a an unstructured conversation."""
from abc import ABC, abstractmethod
from enum import Enum
from typing import Annotated, Literal, Union

from moshi.core.base import Conversation, Message, Role
from pydantic import BaseModel, Field

class ActivityType(str, Enum):
    UNSTRUCTURED = "unstructured"

class BaseActivity(ABC, BaseModel):
    """An activity is a conversation factory."""
    activity_type: ActivityType
    @abstractmethod
    def _init_messages(self) -> list[Message]:
        ...
    def new_conversation(self, uid: str) -> Conversation:
        kind = self.__class__.__name__
        msgs = self._init_messages()
        return Conversation(messages=msgs, uid=uid, kind=kind)

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