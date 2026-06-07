from app.models.payment import ExtractionResult


def test_schema_supports_multiple_payments():
    result = ExtractionResult.model_validate(
        {
            "source_type": "txt",
            "source_filename": "sample.txt",
            "payments": [
                {
                    "vendor": "Acme Supplies",
                    "amount": "450.00",
                    "currency": "USD",
                    "due_date": "2026-07-15",
                    "payment_method": "ACH",
                    "confidence": 0.93,
                    "raw_text_excerpt": "Please ACH $450 to Acme Supplies by July 15.",
                    "notes": "",
                },
                {
                    "vendor": "Beta Logistics",
                    "amount": "2200.50",
                    "currency": "USD",
                    "due_date": None,
                    "payment_method": "wire",
                    "confidence": 0.81,
                    "raw_text_excerpt": "Wire Beta Logistics for freight.",
                    "notes": "No due date provided.",
                },
            ],
        }
    )

    assert len(result.payments) == 2
    assert result.payments[0].vendor == "Acme Supplies"
