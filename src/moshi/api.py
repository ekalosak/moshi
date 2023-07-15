# TODO make stateles api

from fastapi import FastAPI, Depends, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from loguru import logger

from moshi import Message, Conversation
from moshi.auth import firebase_auth

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
    logger.debug(f"Request headers: {request.headers}")
    return "OK"

@app.get("/m/new/{kind}")
async def new_conversation(kind: str, auth: dict = Depends(firebase_auth)):
    """Create a new conversation."""
    logger.debug(f"Servicing request for new conversation of kind: {kind}")
    collection_ref = firebase_db.collection("conversations")
    convo = Conversation.new(kind=kind)
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
