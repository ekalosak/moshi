"""Contains Firebase HTTP auth middleware."""
import contextvars

# from google.cloud import firestore
from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from firebase_admin import auth
from loguru import logger

from moshi.gcloud import GOOGLE_PROJECT

client = auth.AsyncClient(project=GOOGLE_PROJECT)
# logger.debug("Firestore client initialized.")
security = HTTPBearer()
logger.success("Loaded!")

async def firebase_auth(credentials: HTTPAuthorizationCredentials = Depends(security)) -> dict:
    """Middleware to check Firebase authentication in headers.
    Raises:
        - HTTPException 401
    Returns:
        - decoded_token: data from auth service corresponding to credentials.
    """
    try:
        token = credentials.credentials
        decoded_token = await to_thread(
            client.verify_id_token,
            token,
        )
    except auth.InvalidIdTokenError:
        raise HTTPException(status_code=401, detail="Invalid authentication token")
    except auth.ExpiredIdTokenError:
        raise HTTPException(status_code=401, detail="Expired authentication token")
    uid = decoded_token['uid']
    print(type(decoded_token))
    print(decoded_token)
    logger.debug(f"User authenticated uid: {uid}")
    return decoded_token


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
