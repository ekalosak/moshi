import pytest

from moshi import gcloud, secrets

TEST_SECRET_ID = "test-secret-001"

@pytest.mark.asyncio
@pytest.mark.gcloud
async def test_secrets():
    await gcloud.authenticate()
    secret = await secrets.get_secret(TEST_SECRET_ID)
    assert secret == "test"
