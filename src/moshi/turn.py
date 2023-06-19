"""Utilities for interacting with the TURN server"""
import aiohttp
from aiortc import RTCConfiguration, RTCIceServer

from moshi import gcloud

TURN_SECRET_NAME = "metered-turn-server-api-key-001"
logger.info(f"Using TURN_SECRET_NAME={TURN_SECRET_NAME}")

# Free STUN server, thx Google
STUN_SERVERS = [{'urls': ['stun:stun.l.google.com:19302']}]
logger.info(f"Using hardcoded STUN_SERVERS={STUN_SERVERS}")

# https://www.metered.ca/docs/turn-rest-api/get-credential
API_URL = f"https://moshi.metered.live/api/v1/turn/credentials"
logger.debug(f"Using STUN/TURN credentials API_URL={API_URL}")
session = aiohttp.ClientSession(API_URL)
logger.info(f"Created aiohttp session for STUN/TURN hosting API: {session}")

logger.success("Loaded!")

async def _get_turn_server_api_key() -> str:
    """Get API key for metered.ca TURN/STUN servers."""
    return await gcloud.get_secret(secret_id=TURN_SECRET_NAME)

async def _get_turn_servers(api_key: str) -> list[dict[str,str]]:
    """https://www.metered.ca/docs/turn-rest-api/get-credential"""
    async with session.get(API_URL, params={'apiKey': api_key}) as resp:
        logger.debug(f"TURN server response status: {resp.status}")
        return await resp.json()

async def make_ice_config() -> RTCConfiguration:
    ice_servers = []
    # Free STUN servers, use first if possible!
    for srv in STUN_SERVERS:
        ice = RTCIceServer(**srv)
        logger.debug(f"Made RTCIceServer for STUN: {ice}")
        ice_servers.append(ice)
    # Paid for STUN and TURN servers, use if required.
    api_key = await _get_turn_server_api_key()
    paid_servers = await _get_turn_servers()
    ice_servers.extend(paid_servers)
    config = RTCConfiguration(ice_servers)
    logger.info(f"Assembled RTCConfiguration: {config}")
    return config
