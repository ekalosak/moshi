from server import lang

def test_setup_client():
    lang.setup_client()

@pytest.mark.asyncio
@pytest.mark.gcloud
@pytest.parametrize('langcode', ['en_US', 'jp', 'es_MX'])
async def test_get_voice(langcode):
    voice = await get_voice(langcode)
    breakpoint()
    a=1

@pytest.mark.asyncio
@pytest.mark.gcloud
@pytest.mark.parametrize(
    "sentence,langcode",
    [
        pytest.param(
            ("This should start the phrase because I'm speaking continuously for more than a couple seconds, though "
                "your mileage may vary."),
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
            "jp",
            id="Japanese",
        ),
    ]
)
async def test_detect_language(sentence, langcode):
    detlang = await lang.detect_language(sentence)
    assert detlang.startswith(langcode)
