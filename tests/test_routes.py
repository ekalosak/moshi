import asyncio
from unittest import mock

import aiohttp
from aiohttp import web
import pytest

from moshi.server.routes import login

@pytest.mark.asyncio
async def test_login_200(aiohttp_client):
    app = web.Application()
    app.router.add_get('/login', login.login)
    client = await aiohttp_client(app)
    resp = await client.get('/login')
    assert resp.status == 200
