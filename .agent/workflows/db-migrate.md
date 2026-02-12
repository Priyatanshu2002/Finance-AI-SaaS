---
description: Apply database schema migrations to local PostgreSQL or Supabase
---

# Database Migration

Apply schema changes to the local development database or Supabase.

## Local PostgreSQL (Docker)

// turbo
1. Ensure the Postgres container is running:
```
docker-compose up postgres -d
```
Cwd: `c:\Users\Priyatanshu Ghosh\Desktop\AI Projects\Finance AI SaaS`

2. Connect to the local database and run migration SQL:
```
docker exec -i finance-ai-saas-postgres-1 psql -U finance_ai -d finance_ai_db -f /dev/stdin < <migration_file.sql>
```
Replace `<migration_file.sql>` with the path to the SQL migration file.

Alternatively, connect interactively:
```
docker exec -it finance-ai-saas-postgres-1 psql -U finance_ai -d finance_ai_db
```

## Local Connection Details

| Field    | Value          |
|----------|----------------|
| Host     | localhost      |
| Port     | 5432           |
| User     | finance_ai     |
| Password | localdev       |
| Database | finance_ai_db  |

## Supabase (Production)

1. Open the Supabase dashboard SQL Editor at `https://supabase.com/dashboard/project/<project-id>/sql`.
2. Paste the migration SQL and execute.
3. Verify the schema changes in **Table Editor**.

## Schema Files

Migration SQL files should be stored in `backend/database/migrations/` with a timestamp prefix:
```
backend/database/migrations/
  001_initial_schema.sql
  002_add_extraction_results.sql
  ...
```

## Rollback

Always include a rollback section at the bottom of each migration file:
```sql
-- ROLLBACK
-- DROP TABLE IF EXISTS ...;
```
