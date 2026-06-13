# Deployment Guide

This project is deployable without installing local database software. Use Supabase for hosted PostgreSQL, then deploy the Next.js UI and FastAPI API together on Vercel.

## Recommended Deployment Shape

- Database: Supabase Postgres
- App host: Vercel running Next.js and FastAPI
- Secrets: platform environment variables, not `.env` committed to git

Vercel is a strong fit now that the UI is Next.js. The older Streamlit UI remains in the repo as a local prototype, but it is not the primary deployment target.

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

## Vercel Setup

1. Push this project to GitHub.
2. In Vercel, import the GitHub repository.
3. Add these secret environment variables:

```text
OPENAI_API_KEY=...
DATABASE_URL=postgresql+psycopg://...
OPENAI_MODEL=gpt-4o-mini
```

4. Deploy.
5. Confirm `https://YOUR_PROJECT.vercel.app/api/health` returns `{"status":"ok"}`.

## Production Notes

The current app creates the database table at startup. That is acceptable for a portfolio MVP. For production, add Alembic migrations so schema changes are explicit and reversible.

Keep `.env` local only. In deployed environments, use the host platform's environment variable settings.
