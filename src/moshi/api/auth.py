"""Contains Firebase HTTP auth middleware."""
import asyncio
import contextvars
import os

import firebase_admin
from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from firebase_admin import auth as fauth
from google import auth as gauth
from google.auth.transport.requests import Request
from loguru import logger

from moshi.core import storage
from moshi.core.config import GOOGLE_PROJECT

gcreds = contextvars.ContextVar('gcreds')

firebase_app = firebase_admin.initialize_app()
logger.info(f"Firebase authentication initialized: {firebase_app.project_id}")
assert GOOGLE_PROJECT == firebase_app.project_id, f"Initialized auth for unexpected project_id: {firebase_app.project_id}"

security = HTTPBearer()
logger.success("Loaded!")

async def firebase_auth(credentials: HTTPAuthorizationCredentials = Depends(security)) -> dict:
    """Middleware to check Firebase authentication in headers.
    Raises:
        - HTTPException 401
    Returns:
        - decoded_token: data from auth service corresponding to credentials.
    """
    token = credentials.credentials
    try:
        decoded_token = await asyncio.to_thread(
            fauth.verify_id_token,
            token,
        )
    except fauth.InvalidIdTokenError:
        logger.error("Invalid authentication token")
        raise HTTPException(status_code=401, detail="Invalid authentication token")
    except fauth.ExpiredIdTokenError:
        logger.error("Expired authentication token")
        raise HTTPException(status_code=401, detail="Expired authentication token")

    decoded_token['name'] = decoded_token.get('name', 'Unnamed')
    with logger.contextualize(
        uid=decoded_token['uid'],
        uname=decoded_token['name'],
        uemail=decoded_token['email'],
    ):
        logger.debug("User authenticated")
        yield decoded_token


async def is_email_authorized(email: str) -> bool:
    users_ref = storage.firestore_client.collection("authorized_users")
    query = users_ref.where("email", "==", email).limit(1)
    results = await query.get()
    if len(results) > 0:
        logger.info(f"User exists in authorized_users collection: {email}")
        return True
    else:
        logger.info(f"User not in authorized_users collection: {email}")
        return False


async def root_authenticate():
    """Ensure the gcreds context variable is set.
    Raises:
        - google.auth.exceptions.RefreshError if it can't refresh, you'll need to run
            `gcloud auth application-default login`
    """
    try:
        credentials = gcreds.get()
        logger.debug("gcreds already exist.")
    except LookupError:
        logger.debug("gcreds not yet created, initializing...")
        credentials, project_id = gauth.default()
        assert project_id == GOOGLE_PROJECT, f"Unexpected project: {project_id}"
        gcreds.set(credentials)
        logger.info(f"gcreds initialized: {credentials}")
    if not credentials.valid:
        await asyncio.to_thread(credentials.refresh, Request())
    logger.success(
        "Google Cloud credentials refreshed and available via gcloud context var."
    )