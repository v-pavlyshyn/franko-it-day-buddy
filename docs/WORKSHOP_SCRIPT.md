# Сценарій воркшопу (90 хв) — Franko IT Day Buddy

**0–5'** Вступ і демо (живий URL). Кінцева мета: власний /chat з історією.  
**5–15'** Архітектура + Free Tier огляд. Пояснити Firestore vs Cloud SQL.  
**15–30'** Ініціалізація GCP, вмикаємо сервіси, створюємо Firestore.  
**30–55'** Кодимо: /chat, LLM-обгортка, збереження історії.  
**55–70'** CI/CD: Cloud Build → Artifact Registry → Cloud Run (деплой).  
**70–80'** Спостережуваність, ліміти, оптимізація витрат.  
**80–90'** Бонус: MCP-like tools, Q&A, міні-челендж.

### Підказки
- Якщо Vertex AI не працює: USE_VERTEX_MOCK=true і показати відповіді мока.
- Якщо Firestore дає permission denied: перевірити ролі для SA Cloud Run.
- Cloud SQL лише як показ: звернути увагу, що не в Always Free.
