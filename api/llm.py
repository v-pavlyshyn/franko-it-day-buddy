    import os
    from typing import Optional

    USE_VERTEX_MOCK = os.getenv("USE_VERTEX_MOCK", "false").lower() == "true"
    PROJECT_ID = os.getenv("PROJECT_ID")
    LOCATION = os.getenv("LOCATION", "europe-west4")
    MODEL_NAME = os.getenv("MODEL_NAME", "gemini-1.5-flash")

    def _mock_generate(system_prompt: str, context: str, history: str, user_message: str) -> str:
        # Простий фолбек без звернення до Vertex AI (для локальних демо без квот)
        return (
            "📎 [МОК-ВІДПОВІДЬ]

"
            f"System: {system_prompt[:80]}...
"
            f"Context: {context[:120]}...
"
            f"History(last): {history[:120]}...
"
            f"User: {user_message}

"
            "Assistant: Це демонстраційна відповідь без виклику Vertex AI. "
            "Увімкніть Vertex, виставивши USE_VERTEX_MOCK=false в .env."
        )

    def generate_answer(system_prompt: str, context: str, history: str, user_message: str) -> str:
        if USE_VERTEX_MOCK:
            return _mock_generate(system_prompt, context, history, user_message)
        try:
            import vertexai
            from vertexai.generative_models import GenerativeModel
        except Exception as e:
            # якщо бібліотека недоступна — фолбек
            return _mock_generate(system_prompt, context, history, user_message)

        vertexai.init(project=PROJECT_ID, location=LOCATION)
        model = GenerativeModel(MODEL_NAME)

        prompt = (
            f"""{system_prompt}

            Context:
            {context}

            History:
            {history}

            User: {user_message}
            Assistant:"""
        )
        try:
            resp = model.generate_content(prompt)
            # у Vertex AI SDK є властивість text з агрегованою відповіддю
            return (resp.text or "").strip()
        except Exception as e:
            return _mock_generate(system_prompt, context, history, user_message)
