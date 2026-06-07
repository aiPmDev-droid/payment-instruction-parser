from datetime import date, datetime
from enum import Enum

from pydantic import BaseModel, Field


class PaymentMethod(str, Enum):
    ach = "ACH"
    wire = "wire"
    check = "check"
    credit_card = "credit_card"
    paypal = "paypal"
    other = "other"
    unknown = "unknown"


class ExtractedPayment(BaseModel):
    vendor: str = Field(description="Vendor, payee, or supplier requesting payment.")
    amount: float | None = Field(description="Payment amount as a numeric value, excluding currency symbols.")
    currency: str = Field(description="ISO 4217 currency code, such as USD, EUR, or GBP.")
    due_date: date | None = Field(description="Due date for the payment if present.")
    payment_method: PaymentMethod = Field(description="Requested or implied payment method.")
    confidence: float = Field(ge=0, le=1, description="Confidence score for this extracted payment instruction.")
    raw_text_excerpt: str = Field(description="Short source excerpt that supports the extraction.")
    notes: str = Field(description="Ambiguities, missing fields, or extra context useful for finance review.")


class ExtractionResult(BaseModel):
    payments: list[ExtractedPayment]
    source_type: str
    source_filename: str | None = None


class StoredPayment(BaseModel):
    id: int
    vendor: str
    amount: float | None
    currency: str
    due_date: date | None
    payment_method: PaymentMethod
    confidence: float
    raw_text_excerpt: str
    notes: str
    source_filename: str | None
    created_at: datetime

    model_config = {"from_attributes": True}
