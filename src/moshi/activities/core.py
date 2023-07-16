"""Create initial prompt for a an unstructured conversation."""
from abc import ABC, abstractmethod

from moshi.core.base import Conversation, Message, Role

class Activity(ABC):
    @abstractmethod
    def _init_messages(self) -> list[Message]:
        ...
    def new_conversation(self, uid: str) -> Conversation:
        msgs = self._init_messages()
        return Conversation(messages=msgs, uid=uid)

class Unstructured(Activity):
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

def new(kind: str, uid: str) -> Conversation:
    """Initialize a conversation.
    Raises:
        - ValueError if the <kind> isn't supported.
    """
    acts = {'unstructured': Unstructured}
    Act = acts.get(kind)
    if Act is None:
        raise ValueError(f"Invalid activity kind: {kind}\n\tMust be one of {list(acts.keys())}.")
    act = Act()
    return act.new_conversation(uid)
