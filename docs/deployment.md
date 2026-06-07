# Deployment Guide

This project is deployable without installing local database software. Use Supabase for hosted PostgreSQL, then deploy the FastAPI API and Streamlit UI as separate web services.

## Recommended Deployment Shape

- Database: Supabase Postgres
- Backend: Render web service running FastAPI
- Frontend: Render web service running Streamlit
- Secrets: platform environment variables, not `.env` committed to git

Vercel is a strong fit for Next.js. This project currently uses Streamlit, so Render is simpler because it can run both long-lived Python web processes directly.

## Accounts And Local Tools

Required:

- GitHub account
- Supabase account
- Render account
- Git installed locally

Optional:

- Docker Desktop, only for local Docker Compose development
- Python 3.11+, only if running without Docker
- VS Code, for editing

You do not need local Postgres if you use Supabase.

## Supabase Setup

1. Create a new Supabase project.
2. Go to the project dashboard and click **Connect**.
3. Copy a Postgres connection string.
4. For hosted app traffic, prefer the pooler connection if the deployment platform is IPv4-only.
5. Convert the URL to SQLAlchemy format if needed:

```text
postgresql+psycopg://USER:PASSWORD@HOST:PORT/postgres
```

Set this as `DATABASE_URL` in Render.

## Render Setup

1. Push this project to GitHub.
2. In Render, create a new Blueprint from the repository.
3. Render will detect `render.yaml`.
4. Add these secret environment variables:

```text
OPENAI_API_KEY=...
DATABASE_URL=postgresql+psycopg://...
```

5. Deploy `payment-parser-api` first.
6. Copy the API service URL.
7. Set `API_BASE_URL` on `payment-parser-ui` to the API URL.
8. Redeploy the UI service.

## Production Notes

The current app creates the database table at startup. That is acceptable for a portfolio MVP. For production, add Alembic migrations so schema changes are explicit and reversible.

Keep `.env` local only. In deployed environments, use the host platform's environment variable settings.
