import argparse
import asyncio

from aiohttp import web

from moshi.server import make_app

app = make_app()
# app = asyncio.run(make_app())

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Moshi web app")
    parser.add_argument("--cert-file", help="SSL certificate file (for HTTPS)")
    parser.add_argument("--key-file", help="SSL key file (for HTTPS)")
    parser.add_argument(
        "--host", default="127.0.0.1", help="Host for HTTP server (default: 127.0.0.1)"
    )
    parser.add_argument(
        "--port", type=int, default=5000, help="Port for HTTP server (default: 5000)"
    )
    args = parser.parse_args()
    if args.cert_file:
        ssl_context = ssl.SSLContext()
        ssl_context.load_cert_chain(args.cert_file, args.key_file)
    else:
        ssl_context = None
    web.run_app(
        app, access_log=None, host=args.host, port=args.port, ssl_context=ssl_context
    )
