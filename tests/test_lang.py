from unittest import mock

import pytest
from openai.error import RateLimitError

from moshimoshi import lang, Language, Model

def test_language_eq():
    assert Language('fr_FR') == Language('fr_CA')
    assert Language('es_ES') == Language('es_MX')

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
    "sentence,language,model",
    [
        pytest.param(
            "This is an English sentence.", Language.EN_US, Model.TEXTDAVINCI002, id="English"
        ),
        pytest.param(
            "Jé ne parle pás Francais.", Language.FR_CA, Model.TEXTDAVINCI002, id="French"
        ),
        pytest.param(
            "¿Hablas Español tu?", Language.ES_MX, Model.TEXTDAVINCI002, id="Spanish"
        ),
        pytest.param(
            "もしもし", Language.JA_JP, Model.TEXTDAVINCI002, id="Japanese"
        ),
    ]
)
@pytest.mark.xfail(reason="Rate limit", raises=RateLimitError)
def test_recognize_language_openai(sentence, language, model):
    with mock.patch("moshimoshi.think.MODEL", model):
        assert lang.recognize_language(sentence) == language
