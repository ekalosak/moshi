import pytest

from moshi import gcloud


@pytest.mark.asyncio
@pytest.mark.gcloud
async def test_authenticate():
    await gcloud.authenticate()
