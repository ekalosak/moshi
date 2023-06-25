import asyncio
import sys

from google.cloud import firestore

from moshi import auth
from moshi.gcloud import GOOGLE_PROJECT

COLLECTION_NAME = "authorized_users"

try:
    user_fp = sys.argv[1]
except:
    print("Error: usage is `add_authorized_users.py PATH`")
    sys.exit(1)

with open(user_fp, 'r') as f:
    user_emails = f.readlines()
user_emails = [em.strip() for em in user_emails]
assert all("@" in em for em in user_emails)

print(f"Using GCP Project ID: {GOOGLE_PROJECT}")
db = firestore.AsyncClient(project=GOOGLE_PROJECT)
print(f"Using Firestore collection: {COLLECTION_NAME}")
users_ref = db.collection(COLLECTION_NAME)

async def add_users(user_emails: list[str]) -> None:
    batch = db.batch()
    added_emails = []
    for em in user_emails:
        exists = await auth.is_email_authorized(em)
        if exists:
            print(f"User already added: {em}")
            continue
        print(f"Preparing to add user: {em}")
        doc_ref = users_ref.document()
        batch.set(doc_ref, {"email": em})
        added_emails.append(em)
    print(f"Final list: {added_emails}")
    if len(added_emails) == 0:
        print("Nobody to add.")
        sys.exit(0)
    sure = input("Are you sure you'd like to add these users? [y/N]: ").lower()
    if sure == "y":
        await batch.commit()
        print("Added.")
    else:
        print("Aborted.")
        sys.exit(1)

asyncio.run(add_users(user_emails))
