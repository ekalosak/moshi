from aiohttp import web


# Define HTTP endpoints and tooling for authentication
async def healthz(request):
    return web.Response(text="OK")
