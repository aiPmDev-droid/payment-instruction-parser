# Deployment Guide

This project is deployable without installing local database software. Use **Neon** for serverless PostgreSQL, then deploy the Next.js UI and FastAPI API together on Vercel.

## Recommended Deployment Shape

- Database: Neon Postgres
- App host: Vercel running Next.js and FastAPI
- Secrets: platform environment variables, not `.env` committed to git

Vercel is a strong fit now that the UI is Next.js. The older Streamlit UI remains in the repo as a local prototype, but it is not the primary deployment target.

## Accounts And Local Tools

Required:

- GitHub account
- Neon account (free tier)
- Git installed locally

Optional:

- Docker Desktop, only for local Docker Compose development
- Python 3.11+, only if running without Docker
- VS Code, for editing

You do not need local Postgres if you use Neon.

## Database Setup (Neon)

1. Go to [neon.tech](https://neon.tech) and sign up (free tier).
2. Create a new project (choose a region close to you).
3. From the dashboard, copy the **Connection string** (URI format).
4. Convert the URL to SQLAlchemy format:

```text
postgresql+psycopg://USER:PASSWORD@HOST:PORT/DB_NAME?sslmode=require
```

Set this as `DATABASE_URL` in Vercel.

## Vercel Setup

1. Push this project to GitHub.
2. In Vercel, import the GitHub repository.
3. Add these secret environment variables:

```text
GEMINI_API_KEY=...
DATABASE_URL=postgresql+psycopg://...
GEMINI_MODEL=gemini-2.5-flash
```

4. Deploy.
5. Confirm `https://YOUR_PROJECT.vercel.app/api/health` returns `{"status":"ok"}`.

## Production Notes

The current app creates the database table at startup. That is acceptable for a portfolio MVP. For production, add Alembic migrations so schema changes are explicit and reversible.

Keep `.env` local only. In deployed environments, use the host platform's environment variable settings.