from typing import List, Dict, Any
from google.cloud import firestore

db = firestore.Client()

def get_last_messages(user: str, n: int = 5) -> List[Dict[str, Any]]:
    q = (
        db.collection("messages")
        .where("user", "==", user)
        .order_by("ts", direction=firestore.Query.DESCENDING)
        .limit(n)
    )
    docs = list(q.stream())
    # повертаємо у хронологічному порядку (старіші -> новіші)
    res = [d.to_dict() for d in docs][::-1]
    return res

def save_message(user: str, role: str, text: str) -> None:
    db.collection("messages").add(
        {"user": user, "role": role, "text": text, "ts": firestore.SERVER_TIMESTAMP}
    )

def list_faq(limit: int = 20) -> List[Dict[str, Any]]:
    docs = db.collection("faq").limit(limit).stream()
    return [d.to_dict() for d in docs]
