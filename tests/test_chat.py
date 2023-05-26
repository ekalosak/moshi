from unittest import mock

from moshimoshi import Language

def test_chatter_init(chatter):
    assert chatter

@mock.patch('moshimoshi.chat.listen.dialogue_from_mic', lambda: "test")
def test_chatter_get_user_speech(chatter):
    chatter._get_user_speech()
    assert chatter.user_utterance == "test"

@mock.patch('moshimoshi.chat.listen.dialogue_from_mic', lambda: "Hello, Mr. AI.")
@mock.patch('moshimoshi.chat.think.completion_from_assistant', lambda _: "Hello, user.")
def test_chatter_get_assistant_response(chatter):
    chatter._get_user_speech()
    chatter._get_assistant_response()
    assert chatter.assistant_utterance == "Hello, user."

@mock.patch('moshimoshi.chat.listen.dialogue_from_mic', lambda: "Hello, Mr. AI.")
@mock.patch('moshimoshi.chat.think.completion_from_assistant', lambda _: "Hello, user.")
@mock.patch('moshimoshi.chat.speak.say', lambda _: None)
def test_say_assistant_response(chatter):
    chatter._get_user_speech()
    chatter._get_assistant_response()
    chatter._say_assistant_response()

@mock.patch('moshimoshi.chat.listen.dialogue_from_mic', lambda: "Hello, Mr. AI.")
@mock.patch('moshimoshi.chat.lang.recognize_language', lambda _: Language.EN_US)
def test_detect_language(chatter):
    chatter._get_user_speech()
    chatter._detect_language()
    assert chatter.language == Language.EN_US
