from unittest import mock

import pytest

from moshimoshi import lang, Language

def test_language_enum():
    langs = str([l.value for l in lang.Language])
    assert 'en_US' in langs
    assert 'fr_CA' in langs
    assert 'ja_JP' in langs
    assert 'es_MX' in langs

def test_get_language_from_utterance():
    assert lang._get_language_from_utterance("The language code for English is `en_US`") == Language.EN_US

@mock.patch('moshimoshi.lang.think.completion_from_assistant', lambda *a, **kw: ["asdfqwerfr_CAQWETRASDF"])
def test_recognize_language():
    assert lang.recognize_language("Je ne parle pas Francais.") == Language.FR_CA

@pytest.mark.openai
@pytest.mark.parametrize(
    "sentence,language",
    [
        pytest.param(
            "This is an English sentence.", Language.EN_US, id="English"
        ),
        pytest.param(
            "Jé ne parle pás Francais.", Language.FR_CA, id="French"
        ),
        pytest.param(
            "¿Hablas Español tu?", Language.ES_MX, id="Spanish"
        ),
        pytest.param(
            "もしもし", Language.JA_JP, id="Japanese"
        ),
    ]
)
@pytest.mark.xfail(reason="Rate limits from OpenAI", raises=ValueError)  # TODO replace with openaiRaiser
def test_recognize_language_openai(sentence, language):
    assert lang.recognize_language(sentence) == language
