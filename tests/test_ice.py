"""Test the interactive connection establishment module."""
import aiohttp
import pytest
import pytest_asyncio

from moshi import ice

@pytest_asyncio.fixture
async def client():
    print('client')
    async with aiohttp.ClientSession() as client:
        yield client

@pytest.fixture
def ice_client(client):
    print('ice_client')
    with ice.client(client):
        yield

@pytest.mark.asyncio
@pytest.mark.gcloud
@pytest.mark.metered
@pytest.mark.usefixtures("ice_client")
class TestICE:

    async def test_get_ice_config(self):
        """happy path"""
        tok = await ice.get_token()
        cfg = await ice.get_ice_config(tok)
        print(cfg)
        import sys; sys.exit(1)

    async def test_get_ice_secret(self):
        secret = await ice._get_api_secret()
        assert isinstance(secret, str)
        assert len(secret) > 16

    async def test_get_ice_token(self):
        token = await ice.get_token()
        client = ice.aiohttpclient.get()
        headers = {
            "Accept": "application/json",
            "Content-Type": "application/json"
        }
        async with client.post(
            ice.API_PATH_TOKEN_VALID,
            json={'token': token},
            headers=headers,
        ) as resp:
            # https://www.metered.ca/docs/rest-api/post-validate-token-api
            assert resp.status == 200
            valid = await resp.json()
