import logging

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from sqlalchemy import select
from sqlalchemy.exc import OperationalError
from sqlalchemy.orm import Session

from app.db.models import PaymentInstructionRecord
from app.db.session import get_db
from app.models.payment import ExtractionResult, StoredPayment
from app.services.email_loader import read_email_upload
from app.services.extractor import extract_payments

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/payments", tags=["payments"])


@router.post("/extract", response_model=ExtractionResult)
async def extract_payment_file(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
) -> ExtractionResult:
    content = await file.read()
    try:
        source_type, email_text = read_email_upload(file.filename or "upload", content)
        result = extract_payments(email_text, source_type, file.filename)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except RuntimeError as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc

    # Try to persist to database, but don't fail if DB is unavailable
    try:
        for payment in result.payments:
            db.add(
                PaymentInstructionRecord(
                    vendor=payment.vendor,
                    amount=payment.amount,
                    currency=payment.currency,
                    due_date=payment.due_date,
                    payment_method=payment.payment_method.value,
                    confidence=payment.confidence,
                    raw_text_excerpt=payment.raw_text_excerpt,
                    notes=payment.notes,
                    source_filename=file.filename,
                    source_type=source_type,
                    original_text=email_text,
                )
            )
        db.commit()
    except OperationalError as exc:
        logger.warning("Database unavailable, skipping persistence: %s", exc)
        db.rollback()

    return result


@router.get("", response_model=list[StoredPayment])
def list_payments(db: Session = Depends(get_db)) -> list[StoredPayment]:
    try:
        records = db.scalars(
            select(PaymentInstructionRecord).order_by(PaymentInstructionRecord.created_at.desc()).limit(100)
        ).all()
        return records
    except OperationalError as exc:
        logger.warning("Database unavailable, returning empty history: %s", exc)
        return []