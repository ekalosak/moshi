from unittest import mock
import pytest
import openai

from moshi import Message, Model, ModelType, Role
from moshi import think

MODELS = [Model.TEXTADA001, Model.GPT35TURBO0301]

@pytest.mark.openai
@pytest.mark.xfail(
    reason="Rate limits from OpenAI",
    raises=openai.error.RateLimitError,
)
@pytest.mark.parametrize("model", [model for model in MODELS])
def test_completion(model):
    """ Test the chat completion for each model. Importantly, test the abstraction of the completion_from_assistant()
    function over chat_completion (GPT-3.5) and regular completion (text-davinci etc.) model endpoints. """
    msg = 'This is a star spangled test'
    msgs = [
        Message(Role.SYS, f"Respond with '{msg}'")
    ]
    n=1
    resps = think.completion_from_assistant(msgs, n=n, model=model)
    print(resps)
    assert isinstance(resps, list)
    assert len(resps) == n
    resp = resps[0]
    assert isinstance(resp, str)
