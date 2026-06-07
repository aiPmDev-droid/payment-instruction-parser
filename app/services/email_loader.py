from email import policy
from email.parser import BytesParser


SUPPORTED_EXTENSIONS = {".txt", ".eml"}


def read_email_upload(filename: str, content: bytes) -> tuple[str, str]:
    lower_name = filename.lower()
    if lower_name.endswith(".txt"):
        return "txt", content.decode("utf-8", errors="replace")
    if lower_name.endswith(".eml"):
        return "eml", _extract_eml_text(content)
    raise ValueError("Only .txt and .eml files are supported.")


def _extract_eml_text(content: bytes) -> str:
    message = BytesParser(policy=policy.default).parsebytes(content)
    subject = message.get("subject", "")
    sender = message.get("from", "")
    parts: list[str] = []

    if subject:
        parts.append(f"Subject: {subject}")
    if sender:
        parts.append(f"From: {sender}")

    if message.is_multipart():
        for part in message.walk():
            if part.get_content_type() == "text/plain":
                parts.append(part.get_content())
    elif message.get_content_type() == "text/plain":
        parts.append(message.get_content())
    else:
        payload = message.get_payload(decode=True) or b""
        parts.append(payload.decode("utf-8", errors="replace"))

    return "\n\n".join(parts).strip()
