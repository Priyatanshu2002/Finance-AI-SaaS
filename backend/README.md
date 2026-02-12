# Finance AI SaaS — Backend (FastAPI)

Python-based AI/ML core service for financial document extraction.

## Setup

```bash
# Create virtual environment
python -m venv venv

# Activate (Windows)
.\venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run server
uvicorn main:app --reload --port 8000
```

## API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| `POST` | `/api/upload` | Upload a financial document |
| `POST` | `/api/extract` | Trigger extraction on uploaded document |
| `GET` | `/api/extraction/{id}` | Get extraction results |
| `GET` | `/api/documents` | List user's documents |
| `GET` | `/health` | Health check |
