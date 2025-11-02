import csv
from google.cloud import firestore

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
