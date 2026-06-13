# Vercel Deployment

Vercel can deploy the Next.js frontend and FastAPI backend for this project. Supabase should host PostgreSQL.

## What Vercel Hosts

- Next.js finance operations UI
- FastAPI API
- Upload endpoint at `/api/payments/extract`
- History endpoint at `/api/payments`
- Health check at `/api/health`

## Required Services

- Vercel for the Next.js UI and FastAPI backend
- Supabase for hosted PostgreSQL

## Files Added For Vercel

- `pages/index.tsx` is the Next.js frontend.
- `api/index.py` exposes the FastAPI `app` object for Vercel.
- `vercel.json` and `next.config.mjs` route `/api/*` to the FastAPI function.
- `.vercelignore` keeps local-only files out of deployment.
- `requirements.txt` tells Vercel which Python dependencies to install.
- `package.json` tells Vercel which JavaScript dependencies to install.

## Deploy From GitHub

1. Go to Vercel.
2. Import the GitHub repository.
3. Set the project root to this folder if the repo contains other projects.
4. Add environment variables:

```text
GEMINI_API_KEY=...
GEMINI_MODEL=gemini-2.5-flash
DATABASE_URL=postgresql+psycopg://...
```

5. Deploy.
6. Test:

```text
https://YOUR_PROJECT.vercel.app/api/health
```

## Local Vercel Development

```bash
npm install
npm run dev
```

For API testing, make sure `DATABASE_URL` points to Supabase or a local Postgres database.
