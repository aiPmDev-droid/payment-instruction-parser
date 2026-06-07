# How Supabase Fits

Supabase is a managed backend platform built around PostgreSQL. For this project, the most relevant point is simple: the database schema can stay almost identical whether it runs in local Docker Compose or in Supabase.

## What Supabase Provides

- Managed PostgreSQL, so you do not run your own database server.
- A browser SQL editor and table viewer for quick inspection.
- Auth, storage, realtime subscriptions, and edge functions if the product grows.
- Connection strings that work with SQLAlchemy much like a local Postgres URL.

## Local Docker Compose vs Supabase

Docker Compose is best for local development and portfolio demos because it is reproducible and free to run on your machine.

Supabase is best when you want a hosted database, remote demos, shared access, or a production-like environment.

## Migration Path

1. Create a Supabase project.
2. Copy the pooled Postgres connection string.
3. Set `DATABASE_URL` in `.env` to the Supabase SQLAlchemy-compatible URL.
4. Run the FastAPI app. The current startup hook creates the `payment_instructions` table if it does not exist.

For production, replace automatic table creation with Alembic migrations so schema changes are explicit and reviewable.
