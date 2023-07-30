from fastapi.testclient import TestClient
import requests
import pytest

from moshi import ActivityType, Activity, Unstructured
from moshi.api import app

@pytest.mark.parametrize("attyp", [ActivityType.UNSTRUCTURED])
def test_new_convo(attyp: ActivityType, auth_token):
    act = Activity(activity_type=attyp)
    client = TestClient(app)
    print()
    print(act)
    print(act.dict())
    print(act.json())
    print()
    act_ = Activity(**eval(act.json()))
    response = client.post(
        f"/m/new/",
        headers={"Authorization": f"Bearer {auth_token}"},
        data=act.json(),
    )
    print(response.text)
    assert response.status_code == 200
    # TODO check that the conversation was created, and that the messages are correct.
