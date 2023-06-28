import pytest

from moshi import lang


@pytest.mark.gcloud
def test_get_client():
    translation_client = lang._get_client()
    assert translation_client is not None


@pytest.mark.asyncio
@pytest.mark.gcloud
@pytest.mark.parametrize(
    "sentence,langcode",
    [
        pytest.param(
            (
                "This should start the phrase because I'm speaking continuously for more than a couple seconds, though "
                "your mileage may vary."
            ),
            "en",
            id="English",
        ),
        pytest.param(
            "Jé ne parle pás Francais.",
            "fr",
            id="French",
        ),
        pytest.param(
            "¿Hablas Español tu?",
            "es",
            id="Spanish",
        ),
        pytest.param(
            "もしもし",
            "ja",
            id="Japanese",
        ),
    ],
)
async def test_detect_language(sentence, langcode):
    print(f"sentence={sentence}")
    print(f"langcode={langcode}")
    detlang = await lang.detect_language(sentence)
    print(f"detlang={detlang}")
    assert detlang.startswith(langcode)
