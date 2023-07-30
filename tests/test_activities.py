import asyncio
import pytest

from google.cloud import texttospeech

from moshi.core.base import User, Profile, Message
from moshi.utils import ctx
from moshi.core import activities

@pytest.fixture
def event_loop():
    loop = asyncio.get_event_loop()
    yield loop
    loop.close()

@pytest.fixture(autouse=True)
def user():
    user = User(uid="testuid", email="test@test.test")
    tok = ctx.user.set(user)
    try:
        yield
    finally:
        ctx.user.reset(tok)

@pytest.fixture(autouse=True)
def profile():
    profile = Profile(name="testname", lang="en", uid="testuid")
    tok = ctx.profile.set(profile)
    try:
        yield
    finally:
        ctx.profile.reset(tok)

@pytest.mark.gcloud
@pytest.mark.parametrize("activity_type", [activities.ActivityType.UNSTRUCTURED])
def test_new_conversation(event_loop, activity_type):
    act = activities.Activity(activity_type=activity_type)
    event_loop.run_until_complete(act.start())
    assert isinstance(act.messages, list)
    assert isinstance(act.messages[0], Message)
    assert isinstance(act.voice, texttospeech.Voice)
    assert isinstance(act.lang, str)
    assert act.lang == ctx.profile.get().lang