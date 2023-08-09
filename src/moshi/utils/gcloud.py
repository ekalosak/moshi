import asyncio
import contextvars
import os

from google.auth import default
from google.auth.transport.requests import Request
from loguru import logger

GOOGLE_PROJECT = os.getenv("GOOGLE_PROJECT_ID")
logger.info(f"Using Google Cloud project: {GOOGLE_PROJECT}")
if not GOOGLE_PROJECT:
    raise ValueError("GOOGLE_PROJECT_ID is not set! This is a required environment variable.")

gcreds = contextvars.ContextVar("gcreds")

logger.success("Loaded!")


async def authenticate():
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
        credentials, project_id = default()
        assert project_id == GOOGLE_PROJECT, f"Unexpected project: {project_id}"
        gcreds.set(credentials)
        logger.info(f"gcreds initialized: {credentials}")
    if not credentials.valid:
        await asyncio.to_thread(credentials.refresh, Request())
    logger.success(
        "Google Cloud credentials refreshed and available via gcloud context var."
    )
