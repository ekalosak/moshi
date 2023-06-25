import asyncio

import pytest

from moshi import auth

@pytest.mark.asyncio
@pytest.mark.gcloud
async def test_authenticated_email():
    em = "test@test.test"
    authorized = await auth.is_email_authorized(em)
    assert authorized
