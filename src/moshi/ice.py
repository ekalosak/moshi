"""Utilities for interacting with the STUN and TURN server to establish connections."""
import aiohttp
from aiortc import RTCConfiguration, RTCIceServer
import contextvars
from contextlib import contextmanager

from loguru import logger

from moshi import secrets
from moshi.exceptions import SysAuthError

TURN_SECRET_NAME = "metered-turn-server-api-key-001"
logger.info(f"Using TURN_SECRET_NAME={TURN_SECRET_NAME}")

# Free STUN server, thx Google
STUN_SERVERS = [{"urls": ["stun:stun.l.google.com:19302"]}]
logger.info(f"Using hardcoded STUN_SERVERS={STUN_SERVERS}")

# https://www.metered.ca/docs/turn-rest-api/get-credential
API_BASE = "https://moshi.metered.live"
logger.info(f"Using API_BASE={API_BASE}")
API_PATH_CREDENTIALS = f"{API_BASE}/api/v1/turn/credentials"
logger.info(f"Using API_PATH_CREDENTIALS={API_PATH_CREDENTIALS}")
API_PATH_TOKEN = f"{API_BASE}/api/v1/token"
logger.info(f"Using API_PATH_TOKEN={API_PATH_TOKEN}")
API_PATH_TOKEN_VALID = f"{API_BASE}/api/v1/token/validate"
logger.info(f"Using API_PATH_TOKEN_VALID={API_PATH_TOKEN_VALID}")

# NOTE both of these should be private
turnsecret = contextvars.ContextVar("turnsecret")  # set singularly
aiohttpclient = contextvars.ContextVar("aiohttpclient")  # set via ctxmgr

logger.success("Loaded!")


@contextmanager
def client(aiohttp_client):
    """Must provide an aiohttp.ClientSession for all HTTP requests."""
    tok = aiohttpclient.set(aiohttp_client)
    try:
        yield
    finally:
        aiohttpclient.reset(tok)


async def get_token() -> "token":
    """Need different rooms because events on datachannels are broadcast.
    Raises:
        - LookupError if aiohttpclient not set
        - SysAuthError if can't get API secret
    """
    headers = {"Accept": "application/json", "Content-Type": "application/json"}
    api_secret = await _get_api_secret()
    client = aiohttpclient.get()
    async with client.post(
        API_PATH_TOKEN,
        params={"secretKey": api_secret},
        json={"globalToken": "true"},
        headers=headers,
    ) as resp:
        logger.debug(f"{API_PATH_TOKEN} response status: {resp.status}")
        assert resp.status != 404, "Endpoint does not exist"
        if resp.status != 200:
            text = await resp.text()
            logger.error(text)
            raise SysAuthError(
                f"Failed to get a token from {API_PATH_TOKEN}: {resp.status}"
            )
        data = await resp.json()
    return data["token"]


async def token_valid(token) -> bool:
    headers = {"Accept": "application/json", "Content-Type": "application/json"}
    client = aiohttpclient.get()
    async with client.post(
        API_PATH_TOKEN_VALID,
        data={"token": token},
        heasers=headers,
    ) as resp:
        logger.debug(f"{API_PATH_TOKEN_VALID} response status: {resp.status}")
        assert resp.status != 404, "Endpoint does not exist"
        logger.debug(f"resp={resp}")
        return resp.status == 200


async def get_ice_config(token) -> RTCConfiguration:
    """Get ICE config from metered.ca for a user."""
    ice_servers: list[RTCIceServer] = []
    # Free STUN servers, use first if possible!
    for srv in STUN_SERVERS:
        ice = RTCIceServer(**srv)
        ice_servers.append(ice)
    logger.debug(f"Free STUN servers: {ice_servers}")
    # Paid for STUN and TURN servers, use if required.
    paid_servers: list[RTCIceServer] = await _get_turn_servers(token)
    logger.debug(f"Paid STUN and TURN servers: {paid_servers}")
    # Put both together
    ice_servers.extend(paid_servers)
    config = RTCConfiguration(ice_servers)
    logger.info(f"Assembled RTCConfiguration: {config}")
    return config


async def _get_turn_servers(token: str) -> list[RTCIceServer]:
    """https://www.metered.ca/docs/turn-rest-api/get-credential
    Raises:
        - SysAuthError if we can't get to metered.ca
        - LookupError if aiohttpclient not set
    """
    client = aiohttpclient.get()
    async with client.get(API_PATH_CREDENTIALS, params={"apiKey": token}) as resp:
        logger.debug(f"{API_PATH_CREDENTIALS} response status: {resp.status}")
        data = await resp.json()
        if resp.status != 200:
            raise SysAuthError(
                f"Failed to get TURN credentials from {API_PATH_CREDENTIALS}: {data['error']}"
            )
        assert isinstance(data, list)
        assert all(isinstance(dat, dict) for dat in data)
    return [RTCIceServer(**iced) for iced in data]


async def _get_api_secret(retries=3) -> str:
    """Get API key for metered.ca TURN/STUN servers.
    Raises:
        - SysAuthError if timeout backoff fails for GCloud secretsmanager API.
    """
    try:
        return turnsecret.get()
    except LookupError:
        for i in range(retries):
            try:
                secret = await secrets.get_secret(secret_id=TURN_SECRET_NAME)
                turnsecret.set(secret)
                return secret
            except asyncio.TimeoutError as e:
                logger.error(e)
            backoff = 0.1 * i
            logger.debug(f"Backing off {backoff} seconds")
            await asyncio.sleep(backoff)
        raise SysAuthError(
            "Failed to retrieve secret due to timeouts on Google Cloud secretmanager API"
        )
