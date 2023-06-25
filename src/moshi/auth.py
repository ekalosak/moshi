from google.cloud import firestore
from loguru import logger

from moshi.gcloud import GOOGLE_PROJECT

db = firestore.AsyncClient(project=GOOGLE_PROJECT)
users_ref = db.collection("authorized_users")

async def is_email_authorized(email: str) -> bool:
    query = users_ref.where("email", "==", email).limit(1)
    results = await query.get()
    if len(results) > 0:
        logger.info(f"User exists in authorized_users collection: {email}")
        return True
    else:
        logger.info(f"User not in authorized_users collection: {email}")
        return False
