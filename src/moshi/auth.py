import contextvars

from google.cloud import firestore
from loguru import logger

from moshi.gcloud import GOOGLE_PROJECT

gdbclient = contextvars.ContextVar("gdbclient")

logger.success("Loaded!")


def _setup_client():
    """Set the gdbclient ContextVar."""
    try:
        gdbclient.get()
        logger.debug("Firestore client already exists.")
    except LookupError:
        logger.debug("Creating Firestore client...")
        client = firestore.AsyncClient(project=GOOGLE_PROJECT)
        gdbclient.set(client)
        logger.info("Firestore client initialized.")


def _get_client() -> "Client":
    """Get the translation client."""
    _setup_client()
    return gdbclient.get()


async def is_email_authorized(email: str) -> bool:
    db = _get_client()
    users_ref = db.collection("authorized_users")
    query = users_ref.where("email", "==", email).limit(1)
    results = await query.get()
    if len(results) > 0:
        logger.info(f"User exists in authorized_users collection: {email}")
        return True
    else:
        logger.info(f"User not in authorized_users collection: {email}")
        return False
