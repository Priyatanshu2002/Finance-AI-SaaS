---
description: Run the FastAPI backend standalone (without Docker)
---

# Run Backend Standalone

Start the Python FastAPI backend directly for faster iteration during development.

## Prerequisites

- Python 3.11+ installed
- `.env` file exists in project root (copy from `.env.example` if needed)
- Tesseract OCR installed (required by `pytesseract`)
- Local PostgreSQL running on port 5432 (or via Docker: `docker-compose up postgres redis -d`)

## Steps

// turbo
1. Create a virtual environment (skip if already exists):
```
python -m venv venv
```
Cwd: `c:\Users\Priyatanshu Ghosh\Desktop\AI Projects\Finance AI SaaS\backend`

// turbo
2. Activate the virtual environment:
```
.\venv\Scripts\Activate.ps1
```
Cwd: `c:\Users\Priyatanshu Ghosh\Desktop\AI Projects\Finance AI SaaS\backend`

// turbo
3. Install dependencies:
```
pip install -r requirements.txt
```
Cwd: `c:\Users\Priyatanshu Ghosh\Desktop\AI Projects\Finance AI SaaS\backend`

4. Start the FastAPI dev server with auto-reload:
```
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```
Cwd: `c:\Users\Priyatanshu Ghosh\Desktop\AI Projects\Finance AI SaaS\backend`

The `--reload` flag enables hot-reloading on file changes.

5. Verify by hitting the health endpoint:
```
curl http://localhost:8000/health
```

## Notes

- The backend expects `SUPABASE_URL`, `SUPABASE_ANON_KEY`, `ANTHROPIC_API_KEY`, and `REDIS_URL` in`.env`.
- If you only need the backend + DB without the frontend, start dependencies with:
  ```
  docker-compose up postgres redis -d
  ```
- API docs are available at `http://localhost:8000/docs` (Swagger UI) and `http://localhost:8000/redoc`.
