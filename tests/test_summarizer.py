"""Tests for the LLM summarizer module."""

import pytest
from groww_pulse.clustering import Cluster, NormalizedReview
from groww_pulse.summarizer import (
    RateLimiter,
    TokenBudgetExceeded,
    num_tokens_from_messages,
    validate_quotes,
)


def make_review(idx: int, rating: int, text: str) -> NormalizedReview:
    return NormalizedReview(
        doc_id=f"doc_{idx}",
        rating=rating,
        text=text,
        thumbs_up=0,
        app_version="18.0.0",
    )


def test_validate_quotes_valid():
    reviews = [
        make_review(0, 1, "The app crashes on startup every single time."),
        make_review(1, 2, "Cannot withdraw my money, very frustrating."),
    ]
    cluster = Cluster(1, 2, 1.5, representative_reviews=reviews)

    valid_json = {
        "quotes": [
            {"text": "crashes on startup", "doc_id": "doc_0"},
            {"text": "Cannot withdraw my money", "doc_id": "doc_1"},
        ]
    }
    is_valid, _ = validate_quotes(valid_json, cluster)
    assert is_valid


def test_validate_quotes_hallucinated_text():
    reviews = [make_review(0, 1, "The app crashes on startup every single time.")]
    cluster = Cluster(1, 1, 1.0, representative_reviews=reviews)

    invalid_json = {
        "quotes": [{"text": "crashes when you open it", "doc_id": "doc_0"}]
    }
    is_valid, msg = validate_quotes(invalid_json, cluster)
    assert not is_valid
    assert "Hallucinated" in msg


def test_validate_quotes_unknown_doc_id():
    reviews = [make_review(0, 1, "The app crashes on startup every single time.")]
    cluster = Cluster(1, 1, 1.0, representative_reviews=reviews)

    invalid_json = {
        "quotes": [{"text": "crashes on startup", "doc_id": "doc_999"}]
    }
    is_valid, msg = validate_quotes(invalid_json, cluster)
    assert not is_valid
    assert "unknown doc_id" in msg


def test_token_counting():
    messages = [
        {"role": "system", "content": "Hello World"},
        {"role": "user", "content": "How are you?"},
    ]
    tokens = num_tokens_from_messages(messages)
    assert 10 < tokens < 40


@pytest.mark.asyncio
async def test_rate_limiter_budget_exceeded():
    limiter = RateLimiter()
    limiter.tpd = 1000  # very low budget for testing
    limiter.record_usage(900)

    with pytest.raises(TokenBudgetExceeded):
        await limiter.wait_if_needed(200)  # 900 + 200 = 1100 > 1000


@pytest.mark.asyncio
async def test_rate_limiter_daily_request_cap():
    limiter = RateLimiter()
    limiter.rpd = 2
    limiter.requests_today = 2  # already at cap

    with pytest.raises(TokenBudgetExceeded):
        await limiter.wait_if_needed(10)
