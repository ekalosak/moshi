import json
from pprint import pformat, pprint

from fastapi import FastAPI, Depends, HTTPException, Request, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse, FileResponse
from loguru import logger
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import Response

from moshi import activities, util
from moshi.core.storage import firestore_client
from moshi.api.auth import firebase_auth

app = FastAPI()

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
def healthz(request: Request):
    """Health check endpoint"""
    return "OK"

@app.get("/m/new/{kind}")
async def new_conversation(kind: str, user: dict = Depends(firebase_auth)):
    """Create a new conversation."""
    unm = user['name']
    uid = user['uid']
    uem = user['email']
    logger.debug(f"Making new conversation of kind: {kind}")
    collection_ref = firestore_client.collection("conversations")
    convo = activities.new(kind=kind, uid=uid)
    doc_ref = collection_ref.document()
    cid = doc_ref.id
    with logger.contextualize(cid=cid):
        doc_data = convo.asdict()
        logger.debug(f"Creating conversation...")
        result = await doc_ref.set(doc_data)
        logger.info(f"Created new conversation document!")
    return {
        "message": "New conversation created",
        "detail" : {
            "conversation_id": cid,
        }
    }

@app.get("/m/new/{kind}")
async def new_conversation(kind: str, user: dict = Depends(firebase_auth)):
    """Create a new conversation."""
    uid = user['uid']
    logger.debug(f"Making new conversation of kind: {kind}")
    collection_ref = firestore_client.collection("conversations")
    convo = activities.new(kind=kind, uid=uid)
    doc_ref = collection_ref.document()
    cid = doc_ref.id
    with logger.contextualize(cid=cid):
        doc_data = convo.asdict()
        logger.debug(f"Creating conversation...")
        result = await doc_ref.set(doc_data)
        logger.info(f"Created new conversation document!")
    return {
        "message": "New conversation created",
        "detail" : {
            "conversation_id": cid,
        }
    }