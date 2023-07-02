import asyncio
from unittest import mock

import aiohttp
from aiohttp import web
from aiohttp.test_utils import TestServer
import httpx
import pytest
import pytest_asyncio
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from moshi import secrets
from moshi.server import make_app
from moshi.server.routes import login

TEST_EMAIL = "moshi.integration@gmail.com"
EMAIL_PASSWORD_SECRET_ID = "moshi-integration-email-password"


@pytest.fixture(scope="session")
def event_loop():
    policy = asyncio.get_event_loop_policy()
    loop = policy.new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture(scope="module")
async def client():
    async with httpx.AsyncClient() as client:
        yield client


@pytest_asyncio.fixture(scope="module")
async def server():
    app = await make_app()
    srv = TestServer(app, scheme="http", host="localhost", port=8080)
    await srv.start_server()
    yield srv
    await srv.close()


@pytest.fixture(scope="module")
def ffxdriver():
    driver = webdriver.Firefox()
    try:
        yield driver
    finally:
        driver.close()


@pytest.fixture(scope="module")
def drv(ffxdriver):
    drivers = [ffxdriver]
    for driver in drivers:
        yield driver


@pytest.fixture(scope="module")
def wait(drv):
    return WebDriverWait(drv, 1000)


@pytest.fixture(scope="module")
def base_url(server):
    host = "localhost" if server.host == "127.0.0.1" else server.host
    # NOTE localhost literal required for Google OAuth flow.
    return f"{server.scheme}://{host}:{server.port}"


@pytest.mark.asyncio
@pytest.mark.gcloud
async def test_health(server, client):
    res = await client.get("http://localhost:8080/healthz")
    assert res.is_success


@pytest.mark.asyncio
@pytest.mark.slow
@pytest.mark.gcloud
async def test_index_get(server, client):
    res = await client.get("http://localhost:8080/")
    assert res.status_code == 302, "Expected non-logged-in / to redirect to /login"
    res = await client.get("http://localhost:8080/", follow_redirects=True)
    assert res.is_success


@pytest.mark.asyncio
@pytest.mark.gcloud
async def test_login_get(server, client):
    res = await client.get("http://localhost:8080/login")
    assert res.is_success


# NOTE can do the following once email/password auth is implemented (rather than just google oauth)


@pytest.mark.asyncio
@pytest.mark.slow
@pytest.mark.frontend
@pytest.mark.gcloud
async def test_login_flow(base_url, drv, wait):
    url = f"{base_url}/login"
    print(f"GET {url}")
    await asyncio.to_thread(drv.get, url)
    elm = drv.find_element(By.CLASS_NAME, "login-button")
    elm.click()
    await asyncio.sleep(0.5)
    drv.switch_to.window(drv.window_handles[1])  # expect a popup
    try:
        wait.until(EC.presence_of_element_located((By.ID, "identifierId"))).send_keys(
            TEST_EMAIL
        )
        wait.until(EC.presence_of_element_located((By.ID, "identifierNext"))).click()
        # NOTE can't actually do OAuth thru Google in integration tests: https://sqa.stackexchange.com/a/33220
    finally:
        drv.close()  # close the popup
        drv.switch_to.window(drv.window_handles[0])


@pytest.mark.asyncio
@pytest.mark.slow
@pytest.mark.frontend
@pytest.mark.gcloud
@mock.patch("moshi.server.util.NO_SECURITY", True)
async def test_privacy(base_url, drv, wait):
    url = f"{base_url}/privacy"
    print(f"GET {url}")
    await asyncio.to_thread(drv.get, url)
    assert drv.title == "Moshi"
    # NOTE privacy requires auth and google oauth can't be part of integration test so this redirects to /login


@pytest.mark.asyncio
@pytest.mark.slow
@pytest.mark.frontend
@pytest.mark.gcloud
@mock.patch("moshi.server.util.NO_SECURITY", True)
async def test_news(base_url, drv, wait):
    url = f"{base_url}/news"
    print(f"GET {url}")
    await asyncio.to_thread(drv.get, url)
    assert drv.title == "Moshi"
    # NOTE privacy requires auth and google oauth can't be part of integration test so this redirects to /login
    # h1s = drv.find_elements(By.TAG_NAME, 'h1')
    # assert any([h1.text == "News" for h1 in h1s])


# @pytest.mark.asyncio
# @pytest.mark.slow
# @pytest.mark.frontend
# @mock.patch('moshi.server.util.NO_SECURITY', True)
# async def test_index_establish_webrtc(base_url, drv, wait):
#     url = f"{base_url}/"
#     print(f"GET {url}")
#     await asyncio.to_thread(drv.get, url)
#     breakpoint()
#     a=1
