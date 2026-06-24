"""Tests for idempotency logic."""

import json
from unittest.mock import patch, MagicMock
import pytest
from click.testing import CliRunner

from groww_pulse.__main__ import cli
from groww_pulse.receipts import RunReceipt, ReceiptDelivery, ReceiptDeliveryDocs, ReceiptDeliveryGmail

@patch("groww_pulse.receipts.load_receipt")
@patch("groww_pulse.receipts.save_receipt")
@patch("groww_pulse.ingestion.ingest_reviews")
@patch("groww_pulse.clustering.run_clustering_pipeline")
@patch("groww_pulse.summarizer.run_summarization_pipeline")
@patch("groww_pulse.delivery.deliver_to_docs")
@patch("groww_pulse.delivery.deliver_to_gmail")
def test_idempotency_skip_all(mock_deliver_gmail, mock_deliver_docs, mock_summarization, mock_clustering, mock_ingest, mock_save_receipt, mock_load_receipt):
    # Mock pipeline returns
    mock_ingest.return_value = [MagicMock()]
    mock_clustering.return_value = [MagicMock()]
    mock_summarization.return_value = ([], {"total_tokens": 100})
    
    # Mock receipt indicates everything already done
    mock_receipt = RunReceipt(
        idempotency_key="groww:2026-W24",
        run_timestamp="time",
        review_window={},
        reviews_ingested=1,
        clusters_found=1,
        themes_generated=0,
        delivery=ReceiptDelivery(
            google_doc=ReceiptDeliveryDocs(status="appended", doc_id="doc123"),
            gmail=ReceiptDeliveryGmail(status="drafted", draft_id="draft123")
        )
    )
    mock_load_receipt.return_value = mock_receipt
    
    runner = CliRunner()
    result = runner.invoke(cli, ["run", "--week", "2026-W24"])
    
    assert result.exit_code == 0
    assert "Skipped Docs append (already appended with ID: doc123)" in result.output
    assert "Skipped Gmail draft (already drafted with ID: draft123)" in result.output
    
    # Delivery tools should not have been called
    mock_deliver_docs.assert_not_called()
    mock_deliver_gmail.assert_not_called()

@patch("groww_pulse.receipts.load_receipt")
@patch("groww_pulse.receipts.save_receipt")
@patch("groww_pulse.ingestion.ingest_reviews")
@patch("groww_pulse.clustering.run_clustering_pipeline")
@patch("groww_pulse.summarizer.run_summarization_pipeline")
@patch("groww_pulse.delivery.deliver_to_docs")
@patch("groww_pulse.delivery.deliver_to_gmail")
def test_idempotency_partial_retry(mock_deliver_gmail, mock_deliver_docs, mock_summarization, mock_clustering, mock_ingest, mock_save_receipt, mock_load_receipt):
    # Mock pipeline returns
    mock_ingest.return_value = [MagicMock()]
    mock_clustering.return_value = [MagicMock()]
    mock_summarization.return_value = ([], {"total_tokens": 100})
    
    # Mock receipt: Docs succeeded, Gmail pending/failed
    mock_receipt = RunReceipt(
        idempotency_key="groww:2026-W24",
        run_timestamp="time",
        review_window={},
        reviews_ingested=1,
        clusters_found=1,
        themes_generated=0,
        delivery=ReceiptDelivery(
            google_doc=ReceiptDeliveryDocs(status="appended", doc_id="doc123"),
            gmail=ReceiptDeliveryGmail(status="failed")
        )
    )
    mock_load_receipt.return_value = mock_receipt
    
    mock_deliver_gmail.return_value = {"draft_id": "draft456"}
    
    runner = CliRunner()
    result = runner.invoke(cli, ["run", "--week", "2026-W24"])
    
    assert result.exit_code == 0
    assert "Skipped Docs append" in result.output
    assert "Gmail draft created" in result.output
    
    mock_deliver_docs.assert_not_called()
    mock_deliver_gmail.assert_called_once()
    
    # Verify we saved the receipt with the updated state
    assert mock_receipt.delivery.gmail.status == "drafted"
    assert mock_receipt.delivery.gmail.draft_id == "draft456"
