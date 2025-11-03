import os, csv
from google.cloud import firestore

project_id = os.environ.get("PROJECT_ID")
if not project_id:
    raise RuntimeError("PROJECT_ID is not set; export it or fill .env and `export $(grep -v '^#' .env | xargs)`")
db = firestore.Client(project=project_id)

db = firestore.Client()

def main():
    with open('api/sample_faq.csv', newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        batch = db.batch()
        cnt = 0
        for row in reader:
            doc = db.collection('faq').document()
            batch.set(doc, {
                'category': row.get('category'),
                'question': row.get('question'),
                'answer': row.get('answer'),
            })
            cnt += 1
            if cnt % 400 == 0:
                batch.commit()
                batch = db.batch()
        batch.commit()
    print("Seeded FAQ to Firestore.")

if __name__ == "__main__":
    main()
