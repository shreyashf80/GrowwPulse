"""Groww Pulse — PII scrubbing utilities."""

import re

# PII Regex Patterns
# Emails: standard email format
EMAIL_PATTERN = re.compile(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}')

# Phones: Indian (+91) and international formats, allowing spaces/dashes
PHONE_PATTERN = re.compile(r'(?:\+?\d{1,3}[-\s]?)?\(?\d{3}\)?[-\s]?\d{3}[-\s]?\d{4}')

# PAN Card: 5 letters, 4 digits, 1 letter (Indian Tax ID)
PAN_PATTERN = re.compile(r'[A-Z]{5}[0-9]{4}[A-Z]{1}', re.IGNORECASE)

# Aadhaar: 12 digits, often formatted as xxxx xxxx xxxx or xxxx-xxxx-xxxx
AADHAAR_PATTERN = re.compile(r'\b\d{4}[-\s]?\d{4}[-\s]?\d{4}\b')

# UPI ID: pattern like username@bank
UPI_PATTERN = re.compile(r'[a-zA-Z0-9._-]+@[a-zA-Z]{3,}')


def scrub_text(text: str) -> tuple[str, int]:
    """Scrub PII from text.
    
    Returns:
        tuple containing (scrubbed_text, number_of_redactions)
    """
    if not text:
        return text, 0
        
    original_text = text
    redactions = 0
    
    patterns = [
        EMAIL_PATTERN,
        PHONE_PATTERN,
        PAN_PATTERN,
        AADHAAR_PATTERN,
        UPI_PATTERN
    ]
    
    for pattern in patterns:
        text, count = pattern.subn('[REDACTED]', text)
        redactions += count
        
    return text, redactions
