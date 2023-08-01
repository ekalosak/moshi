"""This script initializes the Firestore database with the following collections:
- `transcripts`
- `profiles`
- `config`
- `moshinews`

First it creates the config collection:
- document ID is `supported_langs`:
    - it has 1 element: `lang`: array of strings e.g. `["en-US", "es-MX", ...]` use 20 most popular languages

Second, it creates a default user in Firebase Auth with the following credentials:
- email: `test@test.test`
- password: `testtest`

Third, it creates a default profile for the default user with the following attributes:
- document ID is user uid
- `lang`: `en-US`
- `primary_lang`: `en-US`
- `name`: `Timmy Test`

Fourth, it creates a doc in the moshinews collection:
- `type`: `privacy_policy`
- `body`: `...`
"""

import os
from sys import exit

import firebase_admin
import google.cloud.firestore as firestore
from firebase_admin import auth
from firebase_admin import credentials
from firebase_admin import firestore

PROJECT_ID = "moshi-002"
COLLECTIONS = ["transcripts", "profiles", "config", "moshinews"]
DEFAULT_USER_EMAIL = "test@test.test"
DEFAULT_USER_PASSWORD = "testtest"
DEFAULT_USER_NAME = "Timmy Test"
DEFAULT_USER_LANG = "en-US"
DEFAULT_USER_PRIMARY_LANG = "en-US"

if not os.getenv("FIRESTORE_EMULATOR_HOST"):
    print("FIRESTORE_EMULATOR_HOST not set, exiting.")
    exit(1)
if not os.getenv("FIREBASE_AUTH_EMULATOR_HOST"):
    print("FIREBASE_AUTH_EMULATOR_HOST not set, exiting.")
    exit(1)

SUPPORTED_LANGS = [
    "en-US",
    "es-MX",
    "es-ES",
    "fr-FR",
    "fr-CA",
    "de-DE",
    "it-IT",
    "ja-JP",
    "ko-KR",
    "cmn-CN",
    "cmn-HK",
    "cmn-TW",
]

def _init_firestore():
    """Initialize the Firestore database."""
    db = firestore.client()
    return db

def _init_auth():
    """Initialize the Firebase Auth client."""
    # use the application default credentials
    cred = credentials.ApplicationDefault()
    firebase_admin.initialize_app(cred, {
        'projectId': PROJECT_ID,
    })
    print("Successfully initialized the Firebase Admin SDK.")
    return auth

def _init_config(db):
    """Initialize the config collection."""
    doc_ref = db.collection("config").document("supported_langs")
    doc_ref.set({"langs": SUPPORTED_LANGS})
    print("Successfully initialized the config collection.")

def _init_moshinews(db):
    """Initialize the moshinews collection."""
    doc_ref = db.collection("moshinews").document("privacy_policy")
    doc_ref.set({"body": "..."})
    print("Successfully initialized the moshinews collection.")

def _init_profile(db, uid):
    """Initialize the profiles collection."""
    doc_ref = db.collection("profiles").document(uid)
    doc_ref.set({
        "lang": DEFAULT_USER_LANG,
        "primary_lang": DEFAULT_USER_PRIMARY_LANG,
        "name": DEFAULT_USER_NAME,
    })
    print("Successfully initialized the profiles collection.")

def _init_user(auth):
    """Initialize the default user."""
    try:
        user = auth.create_user(
            email=DEFAULT_USER_EMAIL,
            password=DEFAULT_USER_PASSWORD,
            display_name=DEFAULT_USER_NAME,
        )
    except firebase_admin._auth_utils.EmailAlreadyExistsError:
        print("User already exists.")
        user = auth.get_user_by_email(DEFAULT_USER_EMAIL)
    else:
        print('Successfully created new user.')
    print("Default user: ", user.uid, user.email, user.display_name)
    return user.uid

def main():
    """Initialize the Firestore database."""
    auth = _init_auth()
    uid = _init_user(auth)
    db = _init_firestore()
    _init_profile(db, uid)
    _init_config(db)
    _init_moshinews(db)

if __name__ == "__main__":
    print("START")
    main()
    print("END")
