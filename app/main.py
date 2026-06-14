import logging

from fastapi import FastAPI

from app.api.payments import router as payments_router
from app.db.init import init_db

logger = logging.getLogger(__name__)

app = FastAPI(title="Payment Instruction Parser", version="0.1.0")


@app.on_event("startup")
def startup() -> None:
    try:
        init_db()
        logger.info("Database initialized successfully.")
    except Exception as exc:
        logger.warning("Database unavailable at startup: %s", exc)
        logger.warning("The API will work, but persistence is disabled.")


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/api/health")
def api_health() -> dict[str, str]:
    return {"status": "ok"}


app.include_router(payments_router)
app.include_router(payments_router, prefix="/api")