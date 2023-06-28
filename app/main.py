import argparse
import asyncio

from aiohttp import web

from moshi.server import make_app

async def app_factory():
    return await make_app()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Moshi web app")
    parser.add_argument(
        "--host", default="127.0.0.1", help="Host for HTTP server (default: 127.0.0.1)"
    )
    parser.add_argument(
        "--port", type=int, default=5000, help="Port for HTTP server (default: 5000)"
    )
    args = parser.parse_args()
    app = asyncio.run(app_factory())
    web.run_app(
        app, access_log=None, host=args.host, port=args.port
    )
