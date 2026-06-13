import json
import re
from datetime import date
from typing import Any

from google import genai
from google.genai import types as genai_types

from app.core.config import settings
from app.models.payment import ExtractionResult, ExtractedPayment, PaymentMethod


SYSTEM_PROMPT = """
You are a finance operations extraction assistant.
Extract every distinct payment instruction or invoice payment request from the email.
Return only facts supported by the source text. If a field is missing, use null for dates/amounts,
"unknown" for payment method, USD only when the currency is explicitly USD or strongly implied by US context,
and explain ambiguity in notes. Do not merge multiple invoices into one payment.
""".strip()


# The JSON schema for Gemini's structured output
EXTRACTION_SCHEMA: dict[str, Any] = {
    "type": "object",
    "properties": {
        "payments": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "vendor": {"type": "string", "description": "Vendor, payee, or supplier requesting payment."},
                    "amount": {"type": "number", "description": "Payment amount as a numeric value, excluding currency symbols."},
                    "currency": {"type": "string", "description": "ISO 4217 currency code, such as USD, EUR, or GBP."},
                    "due_date": {"type": "string", "description": "Due date for the payment if present (ISO format YYYY-MM-DD)."},
                    "payment_method": {"type": "string", "description": "Requested or implied payment method: ACH, wire, check, credit_card, paypal, other, or unknown."},
                    "confidence": {"type": "number", "description": "Confidence score for this extracted payment instruction (0.0 to 1.0)."},
                    "raw_text_excerpt": {"type": "string", "description": "Short source excerpt that supports the extraction."},
                    "notes": {"type": "string", "description": "Ambiguities, missing fields, or extra context useful for finance review."},
                },
                "required": ["vendor", "amount", "currency", "due_date", "payment_method", "confidence", "raw_text_excerpt", "notes"],
            },
        }
    },
    "required": ["payments"],
}


def _clean_date(due_date: str | None) -> date | None:
    """Validate and clean a date string. Returns None for invalid/unparseable dates."""
    if not due_date:
        return None
    # Must match YYYY-MM-DD with a valid 4-digit year
    if not re.match(r"^\d{4}-\d{2}-\d{2}$", due_date):
        return None
    try:
        return date.fromisoformat(due_date)
    except (ValueError, TypeError):
        return None


def _clean_payment_data(payments_data: list[dict]) -> list[dict]:
    """Clean and validate raw payment data from the model."""
    valid_methods = {m.value for m in PaymentMethod}
    cleaned = []
    for p in payments_data:
        # Normalize payment_method
        method = p.get("payment_method", "unknown")
        if method not in valid_methods:
            p["payment_method"] = "unknown"

        # Clean due_date: replace invalid strings with None
        raw_date = p.get("due_date")
        p["due_date"] = _clean_date(raw_date) if isinstance(raw_date, str) else raw_date

        cleaned.append(p)
    return cleaned


def extract_payments(email_text: str, source_type: str, source_filename: str | None) -> ExtractionResult:
    if not settings.gemini_api_key:
        raise RuntimeError("GEMINI_API_KEY is not configured.")

    client = genai.Client(api_key=settings.gemini_api_key)

    user_prompt = (
        "Extract payment instructions from this email.\n\n"
        f"Source type: {source_type}\n"
        f"Source filename: {source_filename or 'unknown'}\n\n"
        f"{email_text}"
    )

    response = client.models.generate_content(
        model=settings.gemini_model,
        contents=[
            genai_types.Content(role="user", parts=[genai_types.Part(text=SYSTEM_PROMPT)]),
            genai_types.Content(role="user", parts=[genai_types.Part(text=user_prompt)]),
        ],
        config=genai_types.GenerateContentConfig(
            response_mime_type="application/json",
            response_schema=EXTRACTION_SCHEMA,
            temperature=0.1,
        ),
    )

    raw = response.text
    parsed_json = json.loads(raw)
    payments_data = parsed_json.get("payments", [])

    # Clean and validate fields before building Pydantic models
    payments_data = _clean_payment_data(payments_data)

    result = ExtractionResult(
        payments=[ExtractedPayment(**p) for p in payments_data],
        source_type=source_type,
        source_filename=source_filename,
    )
    return result


def parse_extraction_json(raw_json: str) -> ExtractionResult:
    return ExtractionResult.model_validate(json.loads(raw_json))