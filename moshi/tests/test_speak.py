import pytest

from moshi import speak

@pytest.mark.speak
def test_speak():
    speak.say("test")
