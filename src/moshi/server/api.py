# TODO make stateles api

from fastapi import FastAPI, Depends, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from loguru import logger

from moshi import activities, util
from moshi.core.storage import firestore_client
from moshi.server.auth import firebase_auth

app = FastAPI()

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)
logger.warning("Using permissive CORS for development. In production, only allow requests from known origins.")

@app.get("/healthz")
def healthz(request: Request):
    """Health check endpoint"""
    from pprint import pprint
    pprint(dict(request.headers))
    logger.debug(f"Request from user-agent: {request.headers.get('user-agent', 'unknown')}")
    return "OK"

@app.get("/m/new/{kind}")
async def new_conversation(kind: str, user: dict = Depends(firebase_auth)):
    """Create a new conversation."""
    unm = user['name']
    uid = user['uid']
    uem = user['email']
    with logger.contextualize(user_name=unm, uid=uid, user_email=uem):
        logger.debug(f"Making new conversation of kind: {kind}")
        collection_ref = firestore_client.collection("conversations")
        convo = activities.new(kind=kind, uid=uid)
        logger.info(f"Initializing conversation: {convo}")
        doc_ref = collection_ref.document()
        doc_ref.set(convo.asdict())
        # TODO did = doc_ref['id'] etc. to make the new conversation.
        breakpoint()
    return {
        "message": "New conversation created",
        "document_id": did,
    }

logger.success("Loaded!")
