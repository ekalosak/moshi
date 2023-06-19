import asyncio
import contextvars
import os

from google.auth import default
from google.auth.transport.requests import Request
from google.cloud import secretmanager
from loguru import logger

GOOGLE_PROJECT = os.getenv("GOOGLE_PROJECT_ID", "moshi-002")
logger.info(f"Using Google Cloud project: {GOOGLE_PROJECT}")

SECRET_TIMEOUT = os.getenv("MOSHISECRETTIMEOUT", 2)

gcreds = contextvars.ContextVar("gcreds")
gsecretclient = contextvars.ContextVar("gsecretclient")

logger.success("Loaded!")

def _setup_client():
    """Set the gtransclient ContextVar."""
    try:
        gsecretclient.get()
        logger.debug("Secrets-manager client already exists.")
    except LookupError:
        logger.debug("Creating secrets-manager client...")
        client = secretmanager.SecretManagerServiceAsyncClient()
        gsecretclient.set(client)
        logger.info("Secrets-manager client initialized.")

def _get_client() -> secretmanager.SecretManagerServiceAsyncClient:
    """Get the secrets-manager client."""
    _setup_client()
    return gsecretclient.get()


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

async def get_secret(secret_id: str, project_id=GOOGLE_PROJECT, version_id: str|None=None) -> str:
    """Get a secret from the secrets-manager. If version is None, get latest."""
    client = _get_client()
    logger.debug(f"Getting secret: {secret_id}")
    version_id = version_id or "latest"
    name = f"projects/{project_id}/secrets/{secret_id}/versions/{version_id}"
    logger.debug(f"Constructed name: {name}")
    response = await asyncio.wait_for(
        client.access_secret_version(request={"name": name}),
        timeout=SECRET_TIMEOUT,
    )
    logger.info(f"Retrieved secret: {response.name}")
    secret = response.payload.data.decode("UTF-8")
    logger.debug(f"Secret length: {len(secret)}")
    return secret
