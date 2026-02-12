---
description: Start the full local development stack (Docker Compose)
---

# Start Local Development

Spin up all services (frontend, backend, Redis, PostgreSQL) via Docker Compose.

## Steps

1. Ensure Docker Desktop is running. If not, inform the user to start it manually.

// turbo
2. Navigate to the project root and start all services:
```
docker-compose up --build -d
```
Cwd: `c:\Users\Priyatanshu Ghosh\Desktop\AI Projects\Finance AI SaaS`

// turbo
3. Wait ~15 seconds for services to initialize, then verify all containers are healthy:
```
docker-compose ps
```
Cwd: `c:\Users\Priyatanshu Ghosh\Desktop\AI Projects\Finance AI SaaS`

4. Hit the backend health endpoint to confirm it's up:
```
curl http://localhost:8000/health
```
Expected response: `{"status": "healthy", "service": "finance-ai-backend", "version": "0.1.0"}`

5. Confirm frontend is accessible at `http://localhost:3000`.

## Services

| Service    | URL                     | Port |
|------------|-------------------------|------|
| Frontend   | http://localhost:3000    | 3000 |
| Backend    | http://localhost:8000    | 8000 |
| Redis      | redis://localhost:6379   | 6379 |
| PostgreSQL | localhost:5432           | 5432 |

## Teardown

To stop all services:
```
docker-compose down
```

To stop and **remove volumes** (resets DB data):
```
docker-compose down -v
```
