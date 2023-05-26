import pytest

from moshimoshi import chat

@pytest.fixture
def chatter():
    return chat.Chatter()
