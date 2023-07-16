from google.cloud import firestore
from loguru import logger

from moshi import GOOGLE_PROJECT

logger.debug("Creating Firestore client...")
firestore_client = firestore.AsyncClient(project=GOOGLE_PROJECT)
logger.info(f"Firestore client initialized.")

