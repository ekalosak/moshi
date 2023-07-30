import pytest

from moshi.api.auth import vuid
from moshi.core import activities

@pytest.fixture
def uid():
    return 'test'

@pytest.mark.asyncio
@pytest.mark.parametrize("activity_type", [activities.ActivityType.UNSTRUCTURED])
async def test_new_conversation(uid, activity_type):
    act = activities.Activity(activity_type=activity_type)
    convo = await act.new_conversation(uid)
    assert isinstance(convo, activities.Transcript)