from aiohttp import web
from loguru import logger

# Define HTTP endpoints and tooling for authentication
async def healthz(request):
    logger.debug(f"request: {request}")
    return web.Response(text="OK")
