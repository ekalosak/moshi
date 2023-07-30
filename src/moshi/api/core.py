from contextvars import ContextVar
from enum import Enum
from pprint import pprint

from fastapi import FastAPI, Depends, HTTPException, Request, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse, FileResponse
from loguru import logger
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import Response

from moshi import __version__ as moshi_version
from moshi.core import activities
from moshi.core.activities import ActivityType
from moshi.utils.storage import firestore_client
from moshi.utils.log import setup_loguru
from .auth import firebase_auth, AuthMiddleware
from .routes import offer

app = FastAPI()
app.include_router(offer.router)

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
        pprint(dict(request))  # TODO security problem to print tokens
        logger.trace(f"{request.method} from '{user_agent}' to {request.url}")
        response = await call_next(request)
        return response

app.add_middleware(LogRequestMiddleware)
# app.add_middleware(AuthMiddleware)

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

@app.get("/healthz")
def healthz():
    return "OK"

@app.get("/version")
def version(user: dict = Depends(firebase_auth)):
    print(user)
    return moshi_version

@app.post("/m/new/")
async def new_conversation(activity_type: ActivityType, user: dict = Depends(firebase_auth)):
    """Create a new conversation in the database."""
    uid = user['uid']
    collection_ref = firestore_client.collection("conversations")
    act = activities.Activity(activity_type=activity_type)
    logger.trace(f"Created activity: {act}")
    convo = act.new_conversation()
    logger.trace(f"Created conversation: {convo}")
    doc_ref = collection_ref.document()
    cid = doc_ref.id
    with logger.contextualize(cid=cid):
        logger.trace(f"Creating new conversation document in Firebase...")
        result = await doc_ref.set(convo.asdict())
        logger.trace(f"Created new conversation document!")
    return {
        "message": "New conversation created",
        "detail" : {
            "conversation_id": cid,
        }
    }