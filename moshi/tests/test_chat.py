from unittest import mock

import pytest

from moshi import Language, Model

def test_chatter_init(chatter):
    assert chatter

@pytest.mark.usefixtures("mock_dialogue_from_mic")
def test_chatter_get_user_speech(chatter):
    chatter._get_user_speech()
    assert chatter.user_utterance == "test dialogue_from_mic"

@pytest.mark.usefixtures("mock_dialogue_from_mic")
@pytest.mark.usefixtures("mock_completion_from_assistant")
def test_chatter_get_assistant_response(chatter):
    chatter._get_user_speech()
    chatter._get_assistant_response()
    assert chatter.assistant_utterance == "test completion_from_assistant"

@pytest.mark.usefixtures("mock_dialogue_from_mic")
@pytest.mark.usefixtures("mock_completion_from_assistant")
@pytest.mark.usefixtures("mock_say")
def test_say_assistant_response(chatter):
    chatter._get_user_speech()
    chatter._get_assistant_response()
    chatter._say_assistant_response()

@pytest.mark.usefixtures("mock_dialogue_from_mic")
@mock.patch('moshi.chat.lang.recognize_language', lambda _: Language.EN_US)
def test_detect_language(chatter):
    chatter._get_user_speech()
    chatter._detect_language()
    assert chatter.language == Language.EN_US

@pytest.mark.openai
@pytest.mark.usefixtures("mock_dialogue_from_mic")
@pytest.mark.usefixtures("mock_say")
@mock.patch('moshi.think.MODEL', Model.TEXTADA001)
@mock.patch('moshi.chat.MAX_CHAT_LOOPS', 3)
def test_run(chatter):
    chatter.run()
