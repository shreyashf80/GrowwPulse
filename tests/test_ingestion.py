"""Tests for the ingestion module."""

import asyncio
from datetime import datetime, timedelta, timezone
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from groww_pulse.config import Config
from groww_pulse.ingestion import deduplicate, filter_by_date, ingest_reviews, scrub_pii
from mcp_servers.playstore_reviews.scraper import Review


@pytest.fixture
def sample_reviews():
    now = datetime.now(timezone.utc)
    # R1: Valid, inside window
    r1 = Review(
        review_id="id1", author="User1", rating=5, text="Great app!", 
        timestamp=now.isoformat(), thumbs_up=0, app_version="1.0"
    )
    # R2: Outside window (13 weeks ago)
    r2 = Review(
        review_id="id2", author="User2", rating=4, text="Good", 
        timestamp=(now - timedelta(weeks=13)).isoformat(), thumbs_up=0, app_version="1.0"
    )
    # R3: PII in text
    r3 = Review(
        review_id="id3", author="User3", rating=1, text="Call me 9876543210", 
        timestamp=now.isoformat(), thumbs_up=0, app_version="1.0"
    )
    # R4: Duplicate of R1
    r4 = Review(
        review_id="id1", author="User1", rating=5, text="Great app!", 
        timestamp=now.isoformat(), thumbs_up=0, app_version="1.0"
    )
    return [r1, r2, r3, r4]


def test_filter_by_date(sample_reviews):
    # Window is 12 weeks
    filtered = filter_by_date(sample_reviews, 12)
    # R2 should be dropped
    assert len(filtered) == 3
    assert "id2" not in [r.review_id for r in filtered]


def test_scrub_pii(sample_reviews):
    scrubbed = scrub_pii(sample_reviews)
    # R3 text should be scrubbed
    r3 = next(r for r in scrubbed if r.review_id == "id3")
    assert r3.text == "Call me [REDACTED]"


def test_deduplicate(sample_reviews):
    deduped = deduplicate(sample_reviews)
    # R4 should be dropped since it shares id1
    assert len(deduped) == 3
    ids = [r.review_id for r in deduped]
    assert ids.count("id1") == 1


@pytest.mark.asyncio
@patch("groww_pulse.ingestion.fetch_from_mcp")
async def test_ingest_reviews(mock_fetch, sample_reviews):
    mock_fetch.return_value = sample_reviews
    
    config = Config()
    config.ingestion.window_weeks = 12
    
    result = await ingest_reviews(config)
    
    # After filtering (drops id2), deduping (drops id4), and scrubbing (cleans id3)
    assert len(result) == 2
    ids = [r.review_id for r in result]
    assert "id1" in ids
    assert "id3" in ids
    
    r3 = next(r for r in result if r.review_id == "id3")
    assert "[REDACTED]" in r3.text
