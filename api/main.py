import os
from fastapi import FastAPI, HTTPException
from fastapi.responses import RedirectResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Any

from .llm import generate_answer
from . import mcp_tools

DB_BACKEND = os.getenv("DB_BACKEND", "firestore").lower()
if DB_BACKEND == "sql":
    from . import db_sql as db
else:
    from . import db_firestore as db

PROJECT_ID = os.getenv("PROJECT_ID", "")

app = FastAPI(title="Franko IT Day Buddy")

# Dev CORS (для UI/Pages). У проді налаштуй allow_origins під свій домен.
if os.getenv("ENABLE_DEV_CORS", "false").lower() == "true":
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_methods=["*"],
        allow_headers=["*"],
    )

@app.get("/")
def index():
    return RedirectResponse(url="/docs")

class ChatIn(BaseModel):
    user: str
    message: str

@app.get("/health")
def health():
    return {"ok": True, "db": DB_BACKEND, "project": PROJECT_ID}

@app.get("/tools/list")
def tools_list():
    return mcp_tools.tool_list()

class ToolCall(BaseModel):
    name: str
    args: Dict[str, Any]

@app.post("/tools/call")
def tools_call(tc: ToolCall):
    return mcp_tools.call_tool(tc.name, tc.args)

@app.post("/chat")
def chat(inp: ChatIn):
    if not inp.user or not inp.message:
        raise HTTPException(status_code=400, detail="user and message are required")

    # 1) історія
    last = db.get_last_messages(inp.user, 5)
    history = "\n".join([f"{m['role']}: {m['text']}" for m in last])

    # 2) контекст з FAQ
    faq = db.list_faq(limit=10)
    context_lines = [f"Q: {i.get('question')}\nA: {i.get('answer')}" for i in faq]
    context = "\n\n".join(context_lines) if context_lines else "No FAQ available."

    # 3) системний промпт
    system_prompt = (
        "You are 'Franko IT Day Buddy' — короткий, дружній асистент події Franko IT Day у Львові. "
        "Відповідай українською. Використовуй FAQ нижче, якщо це доречно. "
        "Якщо питання не по темі події — дай коротку корисну відповідь."
    )

    # 4) виклик моделі
    answer = generate_answer(system_prompt, context, history, inp.message)

    # 5) збереження діалогу
    db.save_message(inp.user, "user", inp.message)
    db.save_message(inp.user, "assistant", answer)

    return {"answer": answer}
    