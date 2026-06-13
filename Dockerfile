FROM python:3.11-slim

WORKDIR /app

COPY pyproject.toml ./
RUN pip install --no-cache-dir ".[dev,streamlit]"

COPY . .

EXPOSE 8000 8501
