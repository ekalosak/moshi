from enum import Enum
from pprint import pformat, pprint

from fastapi import FastAPI, Depends, HTTPException, Request, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse, FileResponse
from loguru import logger
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import Response

from moshi import util
from moshi import __version__ as moshi_version
from moshi.core.storage import firestore_client
from .auth import firebase_auth
from .routes import offer

app = FastAPI()
app.include_router(offer.router)

async def on_shutdown():
    logger.info("Shutting down...")
    await offer.shutdown()

app.add_event_handler("shutdown", on_shutdown)

@logger.catch
async def on_startup(app):
    util._setup_loguru()
    # asyncio.get_event_loop().set_exception_handler(util.aio_exception_handler)
    logger.success("Loaded!")

app.add_event_handler("startup", on_startup)

class LogRequestMiddleware(BaseHTTPMiddleware):
    async def dispatch(
        self, request: Request, call_next: RequestResponseEndpoint
    ) -> Response:
        user_agent = request.headers.get("User-Agent", "Unknown agent")
        logger.debug(f"Request from User-Agent: {user_agent}")
        pprint(dict(request))  # TODO security problem to print tokens
        response = await call_next(request)
        return response

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

app.add_middleware(LogRequestMiddleware)

@app.get("/healthz")
def healthz(request: Request, user: dict = Depends(firebase_auth)):
    return "OK"

class ConversationKind(str, Enum):
    unstr = "unstructured"

@app.get("/m/new/{kind}")
async def new_conversation(kind: ConversationKind, user: dict = Depends(firebase_auth)):
    uid = user['uid']
    collection_ref = firestore_client.collection("conversations")
    convo = activities.new(kind=kind, uid=uid)
    doc_ref = collection_ref.document()
    cid = doc_ref.id
    with logger.contextualize(cid=cid):
        logger.trace(f"Creating conversation...")
        result = await doc_ref.set(convo.asdict())
        logger.trace(f"Created new conversation document!")
    return {
        "message": "New conversation created",
        "detail" : {
            "conversation_id": cid,
        }
    }