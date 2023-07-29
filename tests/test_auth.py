import asyncio

import pytest
import requests
from fastapi import HTTPException
from fastapi.testclient import TestClient

from moshi.api import auth
# from moshi import auth
from moshi.api.core import app

# @pytest.mark.asyncio
# @pytest.mark.gcloud
# async def test_authenticated_email():
#     """Tests that the user is in the allowed users list (for closed beta)"""
#     em = "test@test.test"
#     authorized = await auth.is_email_authorized(em)
#     assert authorized

@pytest.fixture
def email():
    return "test@test.test"

@pytest.fixture
def password():
    return "test"

@pytest.fixture
def url():
    """emulator auth service url"""
    return "http://localhost:9099/identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key=dne"

@pytest.mark.asyncio
@pytest.mark.gcloud
async def test_api_auth(email, password, url):
    """Tests Firebase Auth middleware."""
    client = TestClient(app)
    # unauthenticated request against healthz should be ok
    response = client.get("/healthz")
    assert response.status_code == 200
    # unauthenticated request against version should fail
    response = client.get("/version")
    assert response.status_code == 403
    # bad auth token should fail
    auth_token = "badtoken"
    response = client.get("/version", headers={"Authorization": f"Bearer {auth_token}"})
    assert response.status_code == 401
    # get test token
    data = {
        "email": email,
        "password": password,
        "returnSecureToken": True
    }
    response = requests.post(url, json=data)