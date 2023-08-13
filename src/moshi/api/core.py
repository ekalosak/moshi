from enum import Enum
from pprint import pprint

from fastapi import FastAPI, Depends, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from loguru import logger
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import Response

from moshi import __version__ as moshi_version
from moshi.utils.log import setup_loguru
from .auth import firebase_auth
from .routes import offer

app = FastAPI()


async def on_shutdown():
    logger.debug("Shutting down...")
    await offer.shutdown()
    logger.info("Shut down.")


app.add_event_handler("shutdown", on_shutdown)


@logger.catch
async def on_startup():
    logger.debug("Starting up...")
    setup_loguru()
    logger.info("Started up.")


app.add_event_handler("startup", on_startup)


class LogRequestMiddleware(BaseHTTPMiddleware):
    printed_first_healthz = False

    async def dispatch(
        self, request: Request, call_next: RequestResponseEndpoint
    ) -> Response:
        if request.url.path == "/healthz" and self.printed_first_healthz:
            return await call_next(request)
        with logger.contextualize(
            method=request.method, url=str(request.url), useragent=request.headers.get("user-agent"), ip=request.client.host, path=request.url.path, content_type=request.headers.get("content-type"), content_length=request.headers.get("content-length")
        ):
            logger.trace(f"Request received: {request.method} {request.url}")
            if request.url.path == "/healthz":
                self.printed_first_healthz = True
        response = await call_next(request)
        return response


app.add_middleware(LogRequestMiddleware)

# Configure CORS
#   NOTE must be last middleware added.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
    expose_headers=["*"],
)
logger.warning(
    "Using permissive CORS for development. In production, only allow requests from known origins."
)

# NOTE healthz must not require auth so health checks can be performed
logger.debug("Adding healthz route...")
@logger.catch
@app.get("/healthz")
def healthz():
    return "OK"
logger.debug("healthz route added.")

logger.debug("Adding version route...")
@logger.catch
@app.get("/version")
def version(user: dict = Depends(firebase_auth)):
    return moshi_version
logger.debug("version route added.")


logger.debug("Adding index route...")
@logger.catch
@app.get("/")
def index():
    return "Under construction..."
logger.debug("index route added.")

logger.debug("Adding offer route...")
app.include_router(offer.router)
logger.debug("offer route added.")