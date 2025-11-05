# Franko IT Day Buddy — AI мікросервіс на GCP (Cloud Run + Firestore + Cloud Build + Vertex AI)

Навчальний репозиторій для 90-хв воркшопу: збираємо **AI-помічника події** з простим API `/chat`,
історією діалогу у **Firestore**, та генеративними відповідями через **Vertex AI (Google Gen AI)**.

[⬇️ Слайди (PDF)](docs/slides/franko-it-day-buddy-slides.pdf)

> 🎯 Мета: Досвід для студентів **Cloud Run, Cloud Build, Firestore, Vertex AI**. **Cloud SQL** доданий як опційний *Pro-блок*.  
> 🧰 MCP-like «інструменти» реалізовано через HTTP (`/tools/*`).

---

## ⚡ Швидкий старт (локально, 5 кроків)
1. **Авторизація та проєкт**
   ```bash
   gcloud auth login
   gcloud auth application-default login
   gcloud config set project <YOUR_PROJECT_ID>
   ```
2. **Увімкнення сервісів + Firestore (Native)**
   ```bash
   chmod +x scripts/enable_services.sh
   FIRESTORE_LOCATION=eur3 ./scripts/enable_services.sh
   ```
3. **Залежності та конфігурація**
   ```bash
   python3 -m venv .venv && source .venv/bin/activate
   pip install -r api/requirements.txt
   cp .env.example .env
   # Заповніть: PROJECT_ID, LOCATION (напр. europe-central2), MODEL_NAME (gemini-2.5-flash)
   # За потреби: USE_VERTEX_MOCK=true
   ```
4. **(Опційно) Задати FAQ**
   ```bash
   python api/seed_faq.py
   ```
5. **Запуск API**
   ```bash
   export $(grep -v '^#' .env | xargs)
   uvicorn api.main:app --reload --port 8080
   ```

---

## ☁️ Деплой у Cloud Run (Cloud Build)
```bash
gcloud artifacts repositories create demos --repository-format=docker --location=europe --description="workshop repo" || true
PROJECT_ID=$(gcloud config get-value project)
IMAGE=europe-docker.pkg.dev/$PROJECT_ID/demos/itday-buddy:v1
gcloud builds submit --tag $IMAGE
gcloud run deploy itday-buddy --image=$IMAGE --region=europe-central2 --allow-unauthenticated --max-instances=1
```

---

## 🔁 CI варіанти

### Варіант A — **Cloud Build Trigger** (рекомендовано для студентів)
- В  **Cloud Run** підключіть репозиторій GitHub за допомогою **Connect repo** до **Cloud Build** (GitHub App).
- Використовується `cloudbuild.yaml` у корені (уже присутній).  
- При пуші в `main` Cloud Build збере образ і, за потреби, виконає деплой-скрипт.

### Варіант B — **GitHub Actions з OIDC (WIF)**
Файл: `.github/workflows/deploy-cloud-run.yml`. Потрібні секрети в GitHub:
- `GCP_PROJECT_ID` — ID вашого проєкту GCP  
- `GCP_SA_EMAIL` — сервісний акаунт з правами деплою у Cloud Run та доступом до Artifact Registry  
- `GCP_WIF_PROVIDER` — повний шлях до Workload Identity Provider (формату `projects/.../locations/global/workloadIdentityPools/.../providers/...`)

Після цього пуш у `main`:
1) автентифікується через OIDC; 2) збере образ і запушить у Artifact Registry; 3) деплоїть у Cloud Run.

---

## 🧩 Архітектура
```text
(Client) -> /chat (FastAPI) -> Vertex AI (Google Gen AI) (Gemini)
                            -> Firestore (history, faq)
                            -> MCP-like HTTP tools (/tools/*)
Deploy: Cloud Build -> Artifact Registry -> Cloud Run
```

---

## 🔧 Конфігурація (.env)
- `PROJECT_ID` — GCP Project ID  
- `LOCATION` — регіон Vertex AI (Google Gen AI) (напр. `europe-central2`)  
- `MODEL_NAME` — напр. `gemini-2.5-flash`  
- `DB_BACKEND` — `firestore` (за замовчуванням) або `sql`  
- `USE_VERTEX_MOCK` — `true|false` фолбек, якщо немає доступу до Vertex AI (Google Gen AI)  
- `DB_URL` — (опційно для SQL) рядок підключення SQLAlchemy

---

## 🧠 Як працює `/chat`
1) Зчитує останні 5 повідомлень користувача з БД.  
2) Додає короткий контекст-FAQ.  
3) Викликає Vertex AI (Google Gen AI) (або мок).  
4) Зберігає і запит, і відповідь.

---

## 🧰 MCP-like «tools»
- `GET /tools/list` → доступні інструменти  
- `POST /tools/call` → виклик інструмента JSON-ом:
  ```json
  { "name": "get_last_messages", "args": { "user": "anna", "n": 3 } }
  ```

---

## 💪 Pro-блок: Cloud SQL (опційно)
1) Створіть інстанс Postgres у Cloud SQL і БД `chatdb`.  
2) Виконайте міграції з `api/schema.sql`.  
3) Задайте `DB_BACKEND=sql` і `DB_URL`.  
4) Деплойте Cloud Run з `--add-cloudsql-instances`.

---

## 🛡️ Ролі доступу (мінімум)
- Cloud Run SA: `roles/run.admin`, `roles/run.invoker`, `roles/artifactregistry.writer`, `roles/datastore.user`, `roles/aiplatform.user`

---

## 🧹 Як **видалити все** після демо (щоб не було витрат)

Нижче — безпечний чек‑лист. Команди роблять **тільки те**, що ми створювали в цьому воркшопі.
Перед запуском задай змінні (підстав свій проєкт/назви, якщо відрізняються):

```bash
PROJECT_ID=$(gcloud config get-value project)
RUN_REGION=europe-central2
ARTIFACT_REGION=europe
SERVICE=itday-buddy
REPO=demos
SQL_INSTANCE=franko-it-day   # якщо створював Pro‑блок із Cloud SQL; інакше залиш як є
```

### 1) Видалити сервіс Cloud Run
```bash
gcloud run services delete $SERVICE --region=$RUN_REGION --quiet || true
```

### 2) Видалити образи/репозиторій в Artifact Registry
> Якщо **репозиторій `demos` використовуєш лише для цього проєкту**, можна видалити цілий репозиторій.
```bash
# варіант А: видалити лише образи, залишивши репозиторій
gcloud artifacts docker images list $ARTIFACT_REGION-docker.pkg.dev/$PROJECT_ID/$REPO --format='value(package)' | while read -r IMG; do
  DIGEST=$(gcloud artifacts docker images list "$IMG" --format='value(digest)' | head -n1)
  if [[ -n "$DIGEST" ]]; then
    gcloud artifacts docker images delete "$IMG@$DIGEST" --quiet --delete-tags || true
  fi
done

# варіант Б: видалити весь репозиторій (обережно!)
gcloud artifacts repositories delete $REPO --location=$ARTIFACT_REGION --quiet || true
```

### 3) Очистити Firestore (лише колекції воркшопу)
> Це **не видаляє** всю базу — лише документи з `messages` та `faq`.
```bash
# Виконай Python‑скрипт (див. scripts/firestore_cleanup.py)
export PROJECT_ID=$PROJECT_ID
python scripts/firestore_cleanup.py
```

### 4) (Опційно) Видалити Cloud SQL інстанс (якщо створював Pro‑блок)
```bash
gcloud sql instances delete $SQL_INSTANCE --quiet || true
```

### 5) (Опційно) Вимкнути API для перестрахування
> Після вимкнення забуті виклики не згенерують витрати.
```bash
gcloud services disable aiplatform.googleapis.com --quiet || true
gcloud services disable run.googleapis.com         --quiet || true
```

### 6) (Опційно) Видалити сервісний акаунт воркшопу
```bash
gcloud iam service-accounts delete itday-buddy-sa@$PROJECT_ID.iam.gserviceaccount.com --quiet || true
```

### 7) (Опційно) Видалити Cloud Build Trigger
Якщо створював тригер під репозиторій:
```bash
gcloud builds triggers list --format='value(id, name)'
gcloud builds triggers delete <TRIGGER_ID> --quiet
```

> **Порада:** постав **Budget Alerts** у Billing (квота $0 або $1) перед демо — це дає e‑mail/Slack попередження ще до появи рахунків.

---

## 📄 Політики та внесок
- [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md)  
- [CONTRIBUTING.md](CONTRIBUTING.md)  
- [SECURITY.md](SECURITY.md)

---

## 📚 Матеріали для лектора
- [docs/WORKSHOP_SCRIPT.md](docs/WORKSHOP_SCRIPT.md) — сценарій воркшопу
- [docs/slides/franko-it-day-buddy-slides.pdf](docs/slides/franko-it-day-buddy-slides.pdf) — слайди

MIT © 2025 Franko IT Day Workshop
