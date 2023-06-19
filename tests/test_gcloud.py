import pytest

from moshi import gcloud

TEST_SECRET_ID = "test-secret-001"

@pytest.mark.asyncio
@pytest.mark.gcloud
async def test_authenticate():
    await gcloud.authenticate()

@pytest.mark.asyncio
@pytest.mark.gcloud
async def test_secrets():
    await gcloud.authenticate()
    secret = await gcloud.get_secret(TEST_SECRET_ID)
    assert secret == "test"
