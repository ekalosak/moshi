"""This script initializes the Firestore database with the following collections:
- `transcripts`
- `profiles`
- `config`
- `news`

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

Fourth, it creates a doc in the info collection:
- `type`: `privacy_policy`
- `body`: `...`
"""

import os
from sys import exit
from datetime import datetime

import firebase_admin
import google.cloud.firestore as firestore
from firebase_admin import auth
from firebase_admin import credentials
from firebase_admin import firestore

PROJECT_ID = "moshi-3"
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

def _init_info(db):
    """Initialize the moshinews collection."""
    doc_ref = db.collection("info").document()
    doc_ref.set({
        "title": "Privacy Policy",
        "subtitle": "Last updated: 2023-08-09",
        "body": "We take your privacy seriously. What data we do store is encrypted at rest and in flight. We do not share your data with anyone but you and select 3rd party API providers. We do not sell your data. We do not currently use your data for advertising purposes, but may do so in the future in de-identified aggregate.\nWe do use your data to improve our service. We do not currently have a way for you to delete your data in the App, but we will happily do so upon request by email at moshi.feedback@gmail.com. We do not store audio recordings, but we do store transcripts of the conversations you have with Moshi. These transcripts are available to you on the Transcripts page.\nWe do not knowingly collect data from children under 13. If you are a parent or guardian and believe we have collected data from your child, please contact us at moshi.feedback@gmail.com and we will remove it immediately.\nWe may update this privacy policy at any time, please check back for updates.",
        "type": "privacy_policy",
        "timestamp": datetime.now(),
        })
    doc_ref = db.collection("info").document()
    doc_ref.set({
        "title": "Latest updates",
        "subtitle": "Please check for updates regularly.",
        "body": "Please visit www.chatmoshi.com for the latest updates to the Moshi app.",
        "type": "update",
        "timestamp": datetime.now(),
    })
    doc_ref = db.collection("info").document()
    doc_ref.set({
        "title": "Moshi Beta is live!",
        "subtitle": "Thank you for giving Moshi a try!",
        "body": "The Moshi Beta is now live! Thank you for your patience as we continue to improve the service. Please reach out with any suggestions or feedback via the Feedback page.",
        "type": "news",
        "timestamp": datetime.now(),
    })
    print("Successfully initialized the info collection.")

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
    print("Default user: ",  user.email, user.display_name)
    return user.uid

def main():
    """Initialize the Firestore database."""
    auth = _init_auth()
    uid = _init_user(auth)
    db = _init_firestore()
    _init_profile(db, uid)
    _init_config(db)
    _init_info(db)

if __name__ == "__main__":
    print("START")
    main()
    print("END")
