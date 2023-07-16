# TODO make stateles api

from fastapi import FastAPI, Depends, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from loguru import logger

from moshi import Message, Conversation
from moshi.auth import firebase_auth
from moshi.storage import firestore_client

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
async def new_conversation(kind: str, auth: dict = Depends(firebase_auth)):
    """Create a new conversation."""
    logger.debug(f"Servicing request for new conversation of kind: {kind}")
    collection_ref = firestore_client.collection("conversations")
    breakpoint()  # TODO get uid
    uid = foo
    convo = Conversation.new(kind=kind, uid=uid)
    logger.info(f"Initializing conversation: {convo}")
    doc_ref = collection_ref.document()
    doc_ref.set(convo.todict())
    # TODO did = doc_ref['id']
    breakpoint()
    return {
        "message": "New conversation created",
        "document_id": did,
    }

logger.success("Loaded!")
