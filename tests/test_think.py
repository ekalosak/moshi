from unittest import mock

import openai
import pytest

from moshi import Message, Model, ModelType, Role, think

MODELS = [Model.TEXTADA001, Model.GPT35TURBO0301]


@pytest.mark.asyncio
@pytest.mark.openai
@pytest.mark.xfail(
    reason="Rate limits from OpenAI",
    raises=openai.error.RateLimitError,
)
@pytest.mark.parametrize("model", [model for model in MODELS])
async def test_completion(model):
    """Test the chat completion for each model. Importantly, test the abstraction of the completion_from_assistant()
    function over chat_completion (GPT-3.5) and regular completion (text-davinci etc.) model endpoints.
    """
    msg = "This is a star spangled test"
    msgs = [Message(Role.SYS, f"Respond with '{msg}'")]
    n = 1
    resps = await think.completion_from_assistant(msgs, n=n, model=model)
    print(resps)
    assert isinstance(resps, list)
    assert len(resps) == n
    resp = resps[0]
    assert isinstance(resp, str)


parameters = [
    (
        """
        \n\nThIsIsAlSoAmAtCh: extract me
        DontMatchMe: don't extract this
        user: some other response
        """,
        "extract me",
    ),
    (
        """
        \n\nassistant:\n\n\u305d\u306e\u30ec\u30b9\u30c8\u30e9\u30f3\u306f\u3069
        """,
        "\u305d\u306e\u30ec\u30b9\u30c8\u30e9\u30f3\u306f\u3069",
    ),
]


@pytest.mark.parametrize("response,desired", parameters)
def test_completion_scrub(response, desired):
    cleaned = think._clean_completion(response)
    print(f"in: {response}")
    print(f"out: {cleaned}")
    print(f"want: {desired}")
    assert cleaned == desired
