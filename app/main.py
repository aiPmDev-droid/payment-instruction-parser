from fastapi import FastAPI

from app.api.payments import router as payments_router
from app.db.init import init_db

app = FastAPI(title="Payment Instruction Parser", version="0.1.0")


@app.on_event("startup")
def startup() -> None:
    init_db()


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


app.include_router(payments_router)
