# Спрощені «інструменти», які можна викликати через HTTP (MCP-like demo)
# Реальні MCP-сервери можуть інкапсулювати ці функції як tools.
from typing import Any, Dict
import os

DB_BACKEND = os.getenv("DB_BACKEND", "firestore").lower()
if DB_BACKEND == "sql":
    from . import db_sql as db
else:
    from . import db_firestore as db

def tool_list() -> Dict[str, Any]:
    return {
        "tools": [
            {"name": "get_last_messages", "args": {"user": "str", "n": "int=5"}},
            {"name": "save_message", "args": {"user": "str", "role": "str", "text": "str"}},
        ]
    }

def call_tool(name: str, args: Dict[str, Any]) -> Dict[str, Any]:
    if name == "get_last_messages":
        user = args.get("user")
        n = int(args.get("n", 5))
        return {"messages": db.get_last_messages(user, n)}
    elif name == "save_message":
        db.save_message(args["user"], args["role"], args["text"])
        return {"ok": True}
    else:
        return {"error": f"Unknown tool: {name}"}
