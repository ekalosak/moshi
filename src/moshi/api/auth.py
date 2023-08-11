"""Contains Firebase HTTP auth middleware."""
import asyncio
from contextvars import ContextVar

import firebase_admin
from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from firebase_admin import auth as fauth
from google import auth as gauth
from google.auth.transport.requests import Request
from loguru import logger

from moshi.core.base import User, Profile
from moshi.utils import ctx, storage, GOOGLE_PROJECT

DEFAULT_DAILY_CONVO_LIMIT = 5
logger.info(f"DAILY_CONVO_LIMIT: {DEFAULT_DAILY_CONVO_LIMIT}")

gcreds = ContextVar("gcreds")

try:
    firebase_app = firebase_admin.initialize_app()
    logger.info(f"Firebase authentication initialized: {firebase_app.project_id}")
    assert (
        GOOGLE_PROJECT == firebase_app.project_id
    ), f"Initialized auth for unexpected project_id: {firebase_app.project_id}"
except ValueError:
    logger.warning("Firebase authentication already initialized.")

security = HTTPBearer()
logger.success("Loaded!")


async def firebase_auth(
    credentials: HTTPAuthorizationCredentials = Depends(security),
) -> User:
    """Middleware to check Firebase authentication in headers.
    Raises:
        - HTTPException 401
    Returns:
        - User: data from Firebase Auth corresponding to user.
    """
    token = credentials.credentials
    try:
        decoded_token = await asyncio.to_thread(
            fauth.verify_id_token,
            token,
        )
    except fauth.InvalidIdTokenError:
        logger.trace("Invalid authentication token")
        raise HTTPException(status_code=401, detail="Invalid authentication token")
    except fauth.ExpiredIdTokenError:
        logger.trace("Expired authentication token")
        raise HTTPException(status_code=401, detail="Expired authentication token")
    fuser = await asyncio.to_thread(
        fauth.get_user,
        decoded_token["uid"],
    )
    logger.trace(f"User claims: {fuser.custom_claims}")
    try:
        daily_convo_limit = fuser.custom_claims.get("daily_convo_limit", DEFAULT_DAILY_CONVO_LIMIT)
    except AttributeError:
        daily_convo_limit = DEFAULT_DAILY_CONVO_LIMIT
    user = User(
        uid=decoded_token["uid"],
        email=decoded_token["email"],
        daily_convo_limit=daily_convo_limit,
    )
    with logger.contextualize(
        uid=decoded_token["uid"],
        email=decoded_token["email"],
    ):
        token = ctx.user.set(user)
        try:
            logger.trace("User authenticated")
            yield user
        finally:
            ctx.user.reset(token)


async def user_profile(user: User = Depends(firebase_auth)) -> Profile:
    """Middleware to check that user has profile in database.
    Raises:
        - HTTPException 400
    Returns:
        - Profile: data from Firestore corresponding to user's profile.
    """
    try:
        profile = await storage.get_profile(user.uid)
    except KeyError:
        logger.trace("User has no profile")
        raise HTTPException(status_code=400, detail="User has no profile")
    with logger.contextualize(
        name=profile.name,
        lang=profile.lang,
    ):
        token = ctx.profile.set(profile)
        try:
            logger.trace("User has profile")
            yield profile
        finally:
            ctx.profile.reset(token)


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
