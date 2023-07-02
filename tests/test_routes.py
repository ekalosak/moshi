import asyncio
from unittest import mock

import aiohttp
from aiohttp import web
from aiohttp.test_utils import TestServer
import httpx
import pytest
import pytest_asyncio
from selenium import webdriver

from moshi.server import make_app
from moshi.server.routes import login

@pytest.fixture(scope="session")
def event_loop():
    policy = asyncio.get_event_loop_policy()
    loop = policy.new_event_loop()
    yield loop
    loop.close()

@pytest_asyncio.fixture(scope='module')
async def client():
    async with httpx.AsyncClient() as client:
        yield client

@pytest_asyncio.fixture(scope='module')
async def server():
    app = await make_app()
    srv = TestServer(app, scheme='http', host='localhost', port=8080)
    await srv.start_server()
    yield srv
    await srv.close()

@pytest.fixture(scope='module')
def ffxdriver():
    driver = webdriver.Firefox()
    yield driver
    driver.close()

@pytest.fixture(scope="module")
def base_url(server):
    return f"{server.scheme}://{server.host}:{server.port}"

@pytest.mark.asyncio
async def test_health(server, client):
    res = await client.get('http://localhost:8080/healthz')
    assert res.is_success

@pytest.mark.asyncio
async def test_login_get(server, client):
    res = await client.get('http://localhost:8080/login')
    assert res.is_success

@pytest.mark.asyncio
@pytest.mark.slow
async def test_login_flow(base_url, ffxdriver):
    url = f"{base_url}/login"
    print(f"GET {url}")
    await asyncio.to_thread(ffxdriver.get, url)
    breakpoint()
    a=1
