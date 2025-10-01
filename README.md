# Django Log Summary – Quick Start

A tiny Django + DRF API that accepts a log file via **POST**, parses it, calls an LLM for a short summary (mock or real), and lets you **GET** the processed result.

---

## 1) Prerequisites

- Python 3.13+
- pip / venv
- Docker & Docker Compose
- Install all the packages of requirements.txt

```bash
pip install -r requirements.txt
```

> The project loads environment variables from a `.env` at the **project root** (already wired in `settings.py` via `python-dotenv`).

---

## 2) Start PostgreSQL with Docker

Bring up the DB from the provided `docker-compose.yml`:

```bash
docker compose up -d db
```

If you have a native PostgreSQL already on port 5432, the compose file maps the container’s 5432 to **5433** on your host so there’s no conflict.

Check it’s healthy:

```bash
PGPASSWORD=your_password psql -h 127.0.0.1 -p 5433 -U loguser -d logsummary -c "SELECT 1;"
```

> If you change `POSTGRES_USER/POSTGRES_PASSWORD/POSTGRES_DB` in the compose file, recreate the volume: `docker compose down -v && docker compose up -d db`.

---

## 3) Create a virtualenv & install deps

```bash
python -m venv .venv
. .venv/Scripts/activate   # PowerShell: .\.venv\Scripts\Activate.ps1
pip install -r requirements.txt  # or the packages listed above
```

---

## 4) Migrations

Generate and apply migrations for the app models (e.g., `LogJob`):

```bash
python manage.py makemigrations app
python manage.py migrate
```

> The Django settings module is `app.settings` (set in `manage.py`).  
> If you see “relation `app_logjob` does not exist”, it means migrations haven’t been applied yet—run the two commands above.

---

## 5) Run the development server

```bash
python manage.py runserver
```

Server will start at: `http://127.0.0.1:8000/`

---

## 6) API Endpoints

**Base URL placeholder:** `{{baseUrl}} = http://127.0.0.1:8000/api`

Routes are defined as:

- `POST {{baseUrl}}/jobs/` – upload a log file (≤ 1 MB)
- `GET  {{baseUrl}}/jobs/{id}/` – retrieve the processed result

---

## 7) Example requests

### 7.1 Create a job (POST)
Upload a file via multipart/form-data **with trailing slash**:

```bash
curl -F "file=@sample.log" \
     http://127.0.0.1:8000/api/jobs/
```

Example **201** response:
```json
{
  "id": 1,
  "created_at": "2025-10-01T12:34:56Z",
  "filename": "sample.log",
  "size_bytes": 84213,
  "status": "DONE",
  "parsed_preview": { "total_events": 324, "top_errors": [ ... ] },
  "llm_summary": "Mock summary: timeouts to payment provider; add retries and circuit breaker.",
  "llm_cost_usd": null,
  "error_msg": null
}
```

> The upload limit defaults to **1 MB** (configurable via `MAX_LOG_FILE_SIZE_BYTES`). The view enforces it before processing.

### 7.2 Retrieve the result (GET)
```bash
curl http://127.0.0.1:8000/api/jobs/1/
```

Returns the JSON record for job **1** (including `llm_summary`).

---

## 8) LLM behavior

By default, the project runs with a **mock LLM** (`LLM_MOCK=true`) so you can test without any API keys or cost. Set `LLM_MOCK=false` and provide `OPENAI_API_KEY` to call a real model.

---

## 9) Troubleshooting

- **POST redirected / data lost** → Always include the trailing slash (`/api/jobs/`), or set `APPEND_SLASH=False` in settings.
- **Timezone error (`Europe/Germany`)** → The project uses `Europe/Berlin` (valid IANA zone). Ensure your `TIME_ZONE` is correct.
- **Cannot connect to DB** → Confirm your `.env` matches the compose mapping (`DB_HOST=127.0.0.1`, `DB_PORT=5433`) and that the container is running.
- **`relation "app_logjob" does not exist`** → Run migrations (`makemigrations` + `migrate`) against the correct database.
- **Windows & `%` in passwords** → In CMD, `%` is special. Prefer PowerShell or escape `%`, or use a simpler password to test.

---

## 10) Project notes

- Settings module is `app.settings` (configured in `manage.py`).  
- URLs for the API live in `app/urls.py` (see `/api/jobs/` and `/api/jobs/<int:pk>/`).  
- Environment loading is done via `python-dotenv` in `settings.py` (loads `BASE_DIR/.env`).

---

## 11) Clean up

```bash
docker compose down
# or to also remove the Postgres volume/data:
docker compose down -v
```