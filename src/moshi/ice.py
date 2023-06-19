"""Utilities for interacting with the STUN and TURN server to establish connections."""
import aiohttp
from aiortc import RTCConfiguration, RTCIceServer
import contextvars

from loguru import logger

from moshi import secrets
from moshi.exceptions import SysAuthError

TURN_SECRET_NAME = "metered-turn-server-api-key-001"
logger.info(f"Using TURN_SECRET_NAME={TURN_SECRET_NAME}")

# Free STUN server, thx Google
STUN_SERVERS = [{'urls': ['stun:stun.l.google.com:19302']}]
logger.info(f"Using hardcoded STUN_SERVERS={STUN_SERVERS}")

# https://www.metered.ca/docs/turn-rest-api/get-credential
API_URL_BASE = "https://moshi.metered.live"
API_URL_PATH = "/api/v1/turn/credentials"
logger.debug(f"Using STUN/TURN credentials API_URL_BASE={API_URL_BASE}")

iceconfig = contextvars.ContextVar("iceconfig")

logger.success("Loaded!")

async def _setup_ice_config() -> RTCConfiguration:
    """Get ICE config from metered.ca and set the iceconfig CV."""
    ice_servers: list[RTCIceServer] = []
    # Free STUN servers, use first if possible!
    for srv in STUN_SERVERS:
        ice = RTCIceServer(**srv)
        ice_servers.append(ice)
    logger.debug(f"Free STUN servers: {ice_servers}")
    # Paid for STUN and TURN servers, use if required.
    api_key = await _get_turn_server_api_key()
    paid_servers: list[RTCIceServer] = await _get_turn_servers(api_key)
    logger.debug(f"Paid STUN and TURN servers: {paid_servers}")
    # Put both together
    ice_servers.extend(paid_servers)
    config = RTCConfiguration(ice_servers)
    logger.info(f"Assembled RTCConfiguration: {config}")
    iceconfig.set(config)
    return config

async def get_ice_config() -> RTCConfiguration:
    try:
        return iceconfig.get()
    except LookupError:
        return await _setup_ice_config()

async def _get_turn_server_api_key() -> str:
    """Get API key for metered.ca TURN/STUN servers."""
    return await secrets.get_secret(secret_id=TURN_SECRET_NAME)

async def _get_turn_servers(api_key: str) -> list[RTCIceServer]:
    """https://www.metered.ca/docs/turn-rest-api/get-credential"""
    logger.debug(f"Entering context: aiohttp.ClientSession({API_URL_BASE})")
    async with aiohttp.ClientSession(API_URL_BASE) as session:
        logger.info(f"Created aiohttp session for STUN/TURN hosting API: {session}")
        logger.debug(f"Entering context: session.get({API_URL_PATH})")
        async with session.get(API_URL_PATH, params={'apiKey': api_key}) as resp:
            logger.debug(f"TURN server response status: {resp.status}")
            data = await resp.json()
            if resp.status != 200:
                raise SysAuthError(f"Failed to get STUN/TURN servers: {data['error']}")
            ice_dicts: list[dict[str,str]] = data
    return [RTCIceServer(**iced) for iced in ice_dicts]
