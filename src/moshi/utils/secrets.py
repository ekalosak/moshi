import asyncio
import contextvars
import os

from google.cloud import secretmanager
from loguru import logger

from moshi.utils import gcloud

SECRET_TIMEOUT = os.getenv("MOSHISECRETTIMEOUT", 2)
logger.info(f"Using SECRET_TIMEOUT={SECRET_TIMEOUT}")

gsecretclient = contextvars.ContextVar("gsecretclient")


def _setup_client():
    """Set the gtransclient ContextVar."""
    try:
        gsecretclient.get()
        logger.debug("Secretmanager client already exists.")
    except LookupError:
        logger.debug("Creating secretmanager client...")
        client = secretmanager.SecretManagerServiceAsyncClient()
        gsecretclient.set(client)
        logger.info(f"Secretmanager client initialized.")


def _get_client() -> secretmanager.SecretManagerServiceAsyncClient:
    """Get the secrets-manager client."""
    _setup_client()
    return gsecretclient.get()


# TODO this should be a singularly cached function (secrets don't turn over that fast)
async def get_secret(
    secret_id: str,
    project_id=gcloud.GOOGLE_PROJECT,
    version_id: str | None = None,
    decode: str | None = "UTF-8",
) -> str | bytes:
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
    if decode is not None:
        secret = response.payload.data.decode(decode)
    else:
        secret = response.payload.data
    logger.trace(f"Secret length: {len(secret)}")
    logger.trace(f"Secret type: {type(secret)}")
    return secret
