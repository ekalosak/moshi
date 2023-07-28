import os

from loguru import logger

GOOGLE_PROJECT = os.getenv("GOOGLE_PROJECT_ID", "moshi-002")
logger.info(f"Using Google Cloud project: {GOOGLE_PROJECT}")