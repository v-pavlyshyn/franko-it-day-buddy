import os
from typing import List, Dict, Any
from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine

DB_URL = os.getenv("DB_URL")
_engine: Engine = None

def engine() -> Engine:
    global _engine
    if _engine is None:
        if not DB_URL:
            raise RuntimeError("DB_URL is not set for SQL backend")
        _engine = create_engine(DB_URL, pool_pre_ping=True)
    return _engine

def get_last_messages(user: str, n: int = 5) -> List[Dict[str, Any]]:
    sql = text("""
        SELECT user, role, text, ts
        FROM messages
        WHERE user = :user
        ORDER BY ts DESC
        LIMIT :n
    """)
    with engine().begin() as conn:
        rows = conn.execute(sql, {"user": user, "n": n}).mappings().all()
    # у хронологічному порядку
    return list(reversed([dict(r) for r in rows]))

def save_message(user: str, role: str, text: str) -> None:
    sql = text("""
        INSERT INTO messages (user, role, text, ts)
        VALUES (:user, :role, :text, NOW())
    """)
    with engine().begin() as conn:
        conn.execute(sql, {"user": user, "role": role, "text": text})

def list_faq(limit: int = 20) -> List[Dict[str, Any]]:
    sql = text("""
        SELECT question, answer, category FROM faq
        ORDER BY id ASC
        LIMIT :n
    """)
    with engine().begin() as conn:
        rows = conn.execute(sql, {"n": limit}).mappings().all()
    return [dict(r) for r in rows]
