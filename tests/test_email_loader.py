from app.services.email_loader import read_email_upload


def test_read_txt_upload():
    source_type, text = read_email_upload("invoice.txt", b"Please pay Acme $450 by Friday.")

    assert source_type == "txt"
    assert "Acme" in text


def test_read_eml_upload():
    raw = b"""From: billing@example.com
Subject: Invoice 112

Please send ACH payment of $1,200 to Northwind by 2026-07-01.
"""

    source_type, text = read_email_upload("invoice.eml", raw)

    assert source_type == "eml"
    assert "Invoice 112" in text
    assert "Northwind" in text


def test_rejects_unsupported_file():
    try:
        read_email_upload("invoice.pdf", b"data")
    except ValueError as exc:
        assert ".txt and .eml" in str(exc)
    else:
        raise AssertionError("Expected unsupported file to be rejected")
