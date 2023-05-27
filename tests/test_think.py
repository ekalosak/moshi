from unittest import mock
import pytest
import openai

from moshimoshi import Message, Model, ModelType, Role
from moshimoshi import think

@pytest.mark.openai
@pytest.mark.xfail(
    reason="Rate limits from OpenAI",
    raises=openai.error.RateLimitError,
)
@pytest.mark.parametrize("model", [model for model in Model])
def test_completion(model):
    """ Test the chat completion for each model. Importantly, test the abstraction of the completion_from_assistant()
    function over chat_completion (GPT-3.5) and regular completion (text-davinci etc.) model endpoints. """
    msgs = [
        Message(Role.SYS, "Respond with 'This is a star spangled test'")
    ]
    with mock.patch('moshimoshi.think.MODEL', model):
        resp = think.completion_from_assistant(msgs)
    print(resp)
    assert isinstance(resp, str)
