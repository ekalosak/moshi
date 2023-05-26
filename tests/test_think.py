import pytest

from moshimoshi.base import Message, Role
from moshimoshi import think

@pytest.mark.openai
def test_completion():
    msgs = [
        Message(Role.SYS, "Respond with 'I am a monkey'")
    ]
    resp = think.completion_from_assistant(msgs)
    print(resp)
    assert isinstance(resp, str)
