# Payment Instruction Parser

Internal finance tool that extracts structured payment instructions from messy `.txt` and `.eml` emails.

## Stack

Next.js, FastAPI, OpenAI Structured Outputs, PostgreSQL/Supabase, Docker Compose for optional local development.

## Extracted Schema

- `vendor`
- `amount`
- `currency`
- `due_date`
- `payment_method`
- `confidence`
- `raw_text_excerpt`
- `notes`

The API supports multiple payment instructions per email.

## Run Locally

```bash
cp .env.example .env
```

Add your OpenAI API key to `.env`, then run:

```bash
docker compose up --build
```

FastAPI: `http://localhost:8000`

Next.js: run separately with `npm run dev`.

## Run Without Docker

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
uvicorn app.main:app --reload
```

In another terminal:

```bash
streamlit run streamlit_app/Home.py
```

## Run The Vercel-Friendly UI Locally

```bash
npm install
npm run dev
```

Next.js: `http://localhost:3000`

## Test

```bash
pytest
```

## Portfolio Checklist

- Python + FastAPI project skeleton: complete
- ChatGPT API structured extraction: complete
- Output schema with recommended fields: complete
- Next.js upload UI: complete
- PostgreSQL storage: complete
- 10 messy sample emails: complete
- ChatGPT vs regex tradeoff doc: complete
- 1-page case study: complete

## Supabase

See `docs/supabase.md` for how Supabase works as a hosted PostgreSQL option for this project.

## Deployment

See `docs/vercel.md` for the Vercel + Supabase deployment path.
