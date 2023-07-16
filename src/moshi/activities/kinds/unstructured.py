"""Create initial prompt for a an unstructured conversation."""
from moshi import Message

def init_messages() -> list[Message]:
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
