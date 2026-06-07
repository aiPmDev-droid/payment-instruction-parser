# Payment Instruction Parser

Internal finance tool that extracts structured payment instructions from messy `.txt` and `.eml` emails.

## Stack

Python, FastAPI, OpenAI Structured Outputs, Streamlit, PostgreSQL, Docker Compose.

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

Streamlit: `http://localhost:8501`

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

## Test

```bash
pytest
```

## Portfolio Checklist

- Python + FastAPI project skeleton: complete
- ChatGPT API structured extraction: complete
- Output schema with recommended fields: complete
- Streamlit upload UI: complete
- PostgreSQL storage: complete
- 10 messy sample emails: complete
- ChatGPT vs regex tradeoff doc: complete
- 1-page case study: complete

## Supabase

See `docs/supabase.md` for how Supabase works as a hosted PostgreSQL option for this project.

## Deployment

See `docs/deployment.md` for the recommended deployable setup using Supabase and Render.
