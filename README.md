# Finance AI SaaS

## Quick Start

### Prerequisites
- Node.js 18+
- Python 3.11+
- Docker (optional, recommended)

### Option 1: Docker (Recommended)
1. Copy `.env.example` to `.env` and fill in API keys.
2. Run:
   ```bash
   docker-compose up --build
   ```
3. Access Frontend at `http://localhost:3000` and Backend at `http://localhost:8000`.

### Option 2: Manual Setup

#### Frontend
1. Navigate to `frontend/`:
   ```bash
   cd frontend
   npm install
   npm run dev
   ```
2. Access at `http://localhost:3000`.

#### Backend
1. Navigate to `backend/`:
   ```bash
   cd backend
   python -m venv venv
   .\venv\Scripts\Activate.ps1
   pip install -r requirements.txt
   uvicorn main:app --reload --host 0.0.0.0 --port 8000
   ```
2. Access API docs at `http://localhost:8000/docs`.

## Troubleshooting
- If Docker is not found, use Option 2.
- Ensure PostgreSQL and Redis are running for full backend functionality.
