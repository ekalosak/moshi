import pytest

from moshimoshi import speak

@pytest.mark.speak
def test_speak():
    speak.say("test")
