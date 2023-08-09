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
    async def dispatch(
        self, request: Request, call_next: RequestResponseEndpoint
    ) -> Response:
        user_agent = request.headers.get("User-Agent", "Unknown agent")
        logger.trace(f"{request.method} from '{user_agent}' to {request.url}")
        response = await call_next(request)
        return response

app.add_middleware(LogRequestMiddleware)

# Configure CORS
#   NOTE must be last middleware added.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
    expose_headers=["*"],
)
logger.warning("Using permissive CORS for development. In production, only allow requests from known origins.")

# NOTE healthz must not require auth so health checks can be performed
@app.get("/healthz")
def healthz():
    return "OK"

@app.get("/version")
def version(user: dict = Depends(firebase_auth)):
    return moshi_version

app.include_router(offer.router)