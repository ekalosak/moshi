from pprint import pformat, pprint

from fastapi import FastAPI, Depends, HTTPException, Request, File, UploadFile
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import Response

from fastapi.middleware.cors import CORSMiddleware
from loguru import logger

from moshi import activities, util
from moshi.core.storage import firestore_client
from moshi.server.auth import firebase_auth

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

@app.post("/m/next/{cid}")
async def user_utterance(cid: str, utterance: UploadFile, user: dict = Depends(firebase_auth)):
    """Submit recorded audio to Moshi."""
    uid = user['uid']
    collection_ref = firestore_client.collection("conversations")
    doc_ref = collection_ref.document(cid)
    doc = await doc_ref.get()
    if not doc:
        raise HTTPException(
            status_code = 400,
            detail = {"message": f"Document not found: {cid}"}
        )
    elif doc.get('uid') != uid:
        raise HTTPException(
            status_code = 400,
            detail = {"message": f"Document belongs to different user: {doc.get('uid')}"}
        )
    kind = doc.get('kind')
    if not kind:
        raise HTTPException(
            status_code = 500,
            detail = {"message": f"Data format error, 'kind' not found in document."}
        )
    # TODO make chatter/activity
    # TODO submit audio via activity
    # TODO respond with transcripts and utterance
    breakpoint()
    logger.debug(f"Submitting audio for conversation with cid: {cid}")
    return {
        "message": "Audio submitted",
        "detail" : {
            "conversation_id": cid,
        }
    }



logger.success("Loaded!")
