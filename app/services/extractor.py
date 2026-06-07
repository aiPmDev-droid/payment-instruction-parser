import json

from openai import OpenAI

from app.core.config import settings
from app.models.payment import ExtractionResult


SYSTEM_PROMPT = """
You are a finance operations extraction assistant.
Extract every distinct payment instruction or invoice payment request from the email.
Return only facts supported by the source text. If a field is missing, use null for dates/amounts,
"unknown" for payment method, USD only when the currency is explicitly USD or strongly implied by US context,
and explain ambiguity in notes. Do not merge multiple invoices into one payment.
""".strip()


def extract_payments(email_text: str, source_type: str, source_filename: str | None) -> ExtractionResult:
    if not settings.openai_api_key:
        raise RuntimeError("OPENAI_API_KEY is not configured.")

    client = OpenAI(api_key=settings.openai_api_key)
    response = client.responses.parse(
        model=settings.openai_model,
        input=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {
                "role": "user",
                "content": (
                    "Extract payment instructions from this email.\n\n"
                    f"Source type: {source_type}\n"
                    f"Source filename: {source_filename or 'unknown'}\n\n"
                    f"{email_text}"
                ),
            },
        ],
        text_format=ExtractionResult,
    )
    parsed = response.output_parsed
    parsed.source_type = source_type
    parsed.source_filename = source_filename
    return parsed


def parse_extraction_json(raw_json: str) -> ExtractionResult:
    return ExtractionResult.model_validate(json.loads(raw_json))
