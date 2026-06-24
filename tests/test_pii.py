"""Tests for the PII scrubbing utilities."""

import pytest
from groww_pulse.pii import scrub_text

def test_scrub_email():
    text = "Contact me at user@example.com for more details."
    scrubbed, count = scrub_text(text)
    assert scrubbed == "Contact me at [REDACTED] for more details."
    assert count == 1

def test_scrub_phone():
    texts = [
        ("Call +91-9876543210 immediately", "Call [REDACTED] immediately"),
        ("My number is 9876543210", "My number is [REDACTED]"),
        ("Try 123-456-7890 please", "Try [REDACTED] please"),
        ("Or +1 (123) 456-7890", "Or [REDACTED]")
    ]
    for original, expected in texts:
        scrubbed, count = scrub_text(original)
        assert scrubbed == expected
        assert count == 1

def test_scrub_pan():
    text = "My PAN is ABCDE1234F."
    scrubbed, count = scrub_text(text)
    assert scrubbed == "My PAN is [REDACTED]."
    assert count == 1

def test_scrub_aadhaar():
    texts = [
        ("Aadhaar 1234 5678 9012", "Aadhaar [REDACTED]"),
        ("Aadhaar: 1234-5678-9012", "Aadhaar: [REDACTED]"),
        ("ID 123456789012 is mine", "ID [REDACTED] is mine")
    ]
    for original, expected in texts:
        scrubbed, count = scrub_text(original)
        assert scrubbed == expected
        assert count == 1

def test_scrub_upi():
    text = "Send money to shreyash@okhdfcbank"
    scrubbed, count = scrub_text(text)
    assert scrubbed == "Send money to [REDACTED]"
    assert count == 1

def test_no_pii():
    text = "This is a clean review with no sensitive data."
    scrubbed, count = scrub_text(text)
    assert scrubbed == text
    assert count == 0

def test_mixed_pii():
    text = "Name: John, Email: john@test.com, Phone: 9998887776, PAN: QWERT9876Y"
    scrubbed, count = scrub_text(text)
    assert scrubbed == "Name: John, Email: [REDACTED], Phone: [REDACTED], PAN: [REDACTED]"
    assert count == 3
