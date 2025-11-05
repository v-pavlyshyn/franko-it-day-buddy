# scripts/firestore_cleanup.py
# Deletes only workshop collections: messages & faq
import os, sys, time
from google.cloud import firestore

PROJECT_ID = os.getenv("PROJECT_ID") or os.getenv("GOOGLE_CLOUD_PROJECT")
if not PROJECT_ID:
    print("Set PROJECT_ID env first"); sys.exit(1)

db = firestore.Client(project=PROJECT_ID)

def delete_collection(coll_name: str, batch_size: int = 300):
    print(f"Deleting collection: {coll_name}")
    while True:
        docs = list(db.collection(coll_name).limit(batch_size).stream())
        if not docs:
            break
        batch = db.batch()
        for d in docs:
            batch.delete(d.reference)
        batch.commit()
        print(f"  deleted {len(docs)} docs...")
        time.sleep(0.2)
    print(f"Done {coll_name}")

if __name__ == "__main__":
    delete_collection("messages")
    delete_collection("faq")
    print("Firestore cleanup complete ✅")
