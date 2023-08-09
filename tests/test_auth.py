"""Tests API Firebase auth.
NOTE: This test requires a running Firebase emulator.
NOTE: This test requires a test user in the Firebase auth service.
NOTE: You must set FIREBASE_AUTH_EMULATOR_HOST="127.0.0.1:9099" in your environment.
"""
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


@pytest.mark.asyncio
@pytest.mark.gcloud
async def test_api_auth(auth_token):
    """Tests Firebase Auth middleware."""
    client = TestClient(app)
    response = client.get("/healthz")
    assert response.status_code == 200
    response = client.get("/version")
    assert response.status_code == 403
    response = client.get("/version", headers={"Authorization": f"Bearer badtoken"})
    assert response.status_code == 401
    response = client.get("/version", headers={"Authorization": f"Bearer {auth_token}"})
    print(response.json())
    assert response.status_code == 200
