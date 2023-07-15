# TODO make stateles api

from fastapi import FastAPI, Depends, HTTPException
from loguru import logger

from moshi import Message, Conversation

app = FastAPI()
logger.success("Loaded!")

@app.get("/healthz")
def healthz():
    """Health check endpoint"""
    return "OK"

@app.get("/m/{kind}/new")
async def new_conversation(kind: str, auth: dict = Depends(firebase_auth)):
    """Create a new conversation."""
    collection_ref = firebase_db.collection("conversations")
    convo = Conversation.new(kind=kind)
    logger.info(f"Initializing conversation: {convo}")
    doc_ref = collection_ref.document()
    doc_ref.set(convo.todict())
    # TODO did = doc_ref['id']
    breakpoint()
    return {
        "message": "New conversation created",
        "detail": {
            "did": did,
        }
    }
