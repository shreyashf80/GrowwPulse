"""Tests for the receipts module and idempotency logic."""

import json
from pathlib import Path
from groww_pulse.receipts import RunReceipt, ReceiptDelivery, ReceiptDeliveryDocs, ReceiptDeliveryGmail
from groww_pulse.receipts import save_receipt, load_receipt, get_receipt_path

def test_receipt_serialization():
    receipt = RunReceipt(
        idempotency_key="groww:2026-W24",
        run_timestamp="2026-06-09T09:12:34+05:30",
        review_window={"start": "2026-03-30", "end": "2026-06-09"},
        reviews_ingested=100,
        clusters_found=5,
        themes_generated=3,
        delivery=ReceiptDelivery(
            google_doc=ReceiptDeliveryDocs(status="appended", doc_id="doc123"),
            gmail=ReceiptDeliveryGmail(status="drafted", draft_id="draft123")
        ),
        llm_usage={"total_tokens": 1000}
    )
    
    data = receipt.to_dict()
    assert data["idempotency_key"] == "groww:2026-W24"
    assert data["delivery"]["google_doc"]["status"] == "appended"
    assert data["delivery"]["gmail"]["draft_id"] == "draft123"
    
    restored = RunReceipt.from_dict(data)
    assert restored.idempotency_key == "groww:2026-W24"
    assert restored.delivery.google_doc.status == "appended"
    assert restored.delivery.gmail.status == "drafted"

def test_save_and_load_receipt(tmp_path):
    receipt = RunReceipt(
        idempotency_key="groww:2026-W25",
        run_timestamp="2026-06-16T09:12:34+05:30",
        review_window={},
        reviews_ingested=50,
        clusters_found=2,
        themes_generated=1
    )
    
    storage_path = str(tmp_path)
    
    # Save it
    save_receipt(storage_path, "2026-W25", receipt)
    
    # Check if file exists
    assert get_receipt_path(storage_path, "2026-W25").exists()
    
    # Load it
    loaded = load_receipt(storage_path, "2026-W25")
    assert loaded is not None
    assert loaded.idempotency_key == "groww:2026-W25"
    assert loaded.reviews_ingested == 50
    assert loaded.delivery.google_doc.status == "pending"

def test_load_nonexistent_receipt(tmp_path):
    storage_path = str(tmp_path)
    loaded = load_receipt(storage_path, "2026-W99")
    assert loaded is None
