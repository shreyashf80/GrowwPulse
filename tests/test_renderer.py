"""Tests for the renderer module."""

import pytest
from groww_pulse.renderer import render_docs_payload, render_email_payload, EmailPayload
from groww_pulse.config import Config, ProductConfig, IngestionConfig, ClusteringConfig, LLMConfig, DeliveryConfig, ReceiptsConfig

@pytest.fixture
def mock_config():
    return Config(
        product=ProductConfig(name="GrowwTest", play_store_app_id="com.test"),
        ingestion=IngestionConfig(window_weeks=4, max_reviews=100),
        clustering=ClusteringConfig(umap_n_components=5, umap_n_neighbors=15, hdbscan_min_cluster_size=10, hdbscan_min_samples=5),
        llm=LLMConfig(model="test-model", temperature=0.1, max_tokens=100, quote_validation=False),
        delivery=DeliveryConfig(google_doc_id="test_doc_123", email_recipients=["test@example.com"], draft_only=True),
        receipts=ReceiptsConfig(storage_path="/tmp")
    )

@pytest.fixture
def mock_themes():
    return [
        {
            "theme_name": "Test Theme",
            "review_count": 10,
            "avg_rating": 4.5,
            "description": "Test description",
            "quotes": [
                {"text": "Great app", "rating": 5}
            ],
            "action_ideas": [
                {"title": "Do this", "detail": "Because reasons"}
            ]
        }
    ]

def test_render_docs_payload(mock_themes, mock_config):
    text = render_docs_payload(mock_themes, "2026-W24", mock_config)
    assert isinstance(text, str)
    
    assert "GrowwTest — Weekly Review Pulse (2026-W24)" in text
    assert "Test Theme (10 reviews, Avg Rating: 4.5)" in text
    assert "Test description" in text
    assert "> \"Great app\" (5/5)" in text
    assert "- Do this: Because reasons" in text

def test_render_email_payload(mock_themes, mock_config):
    email = render_email_payload(mock_themes, "2026-W24", mock_config, mock_config.delivery.google_doc_id)
    
    assert isinstance(email, EmailPayload)
    assert email.subject == "GrowwTest Review Pulse — 2026-W24"
    
    # Check HTML
    assert "GrowwTest" in email.html_body
    assert "<strong>2026-W24</strong>" in email.html_body
    assert "<li><strong>Test Theme</strong> (10 reviews)</li>" in email.html_body
    assert "href=\"https://docs.google.com/document/d/test_doc_123\"" in email.html_body
    
    # Check text
    assert "GrowwTest" in email.text_body
    assert "- Test Theme (10 reviews)" in email.text_body
    assert "https://docs.google.com/document/d/test_doc_123" in email.text_body
