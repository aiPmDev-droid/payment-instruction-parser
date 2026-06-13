# Payment Instruction Parser Case Study

## Problem

Finance teams often receive payment instructions through messy email threads, forwarded invoices, and informal reminders. Manual extraction creates delays and increases the risk of missing due dates, vendors, or payment methods.

## Solution

Payment Instruction Parser is an internal finance tool that accepts `.txt` and `.eml` email uploads, extracts one or more payment instructions, and stores the structured results in PostgreSQL for review. The Streamlit interface gives finance operators a simple workflow: upload an email, inspect extracted fields, and review recent extraction history.

## Product Choices

The app uses FastAPI for the backend because it provides a clean API boundary between extraction, storage, and the UI. Streamlit keeps the operator interface lightweight and fast to iterate. PostgreSQL supports an audit-friendly history table, while Docker Compose makes the portfolio demo reproducible.

The extraction layer uses Google Gemini Structured Outputs so model responses match a strict schema instead of returning loose JSON. Each extracted payment includes vendor, amount, currency, due date, payment method, confidence, supporting source excerpt, and notes.

## Impact

The tool reduces manual data entry and creates a more reliable review queue for accounts payable. It is especially useful when a single email contains multiple payment requests or when emails use inconsistent wording.

## Future Improvements

Next steps include human approval status, invoice attachment parsing, Supabase deployment, validation rules for suspicious payment changes, and dashboards for payment volume and extraction accuracy.
