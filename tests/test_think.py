import pytest

from moshimoshi.base import Message, Role
from moshimoshi import think

@pytest.mark.openai
@pytest.mark.xfail(reason="Rate limits from OpenAI")
def test_completion():
    msgs = [
        Message(Role.SYS, "Respond with 'I am a monkey'")
    ]
    resp = think.completion_from_assistant(msgs)
    print(resp)
    assert isinstance(resp, str)
