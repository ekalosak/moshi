import pytest

from moshi import server

@pytest.mark.asyncio
async def test_make_app():
    app = await server.make_app()
