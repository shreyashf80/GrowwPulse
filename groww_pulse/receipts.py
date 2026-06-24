import json
from pathlib import Path
from typing import Dict, Any, Optional
import dataclasses

@dataclasses.dataclass
class ReceiptDeliveryDocs:
    status: str = "pending" # pending, appended, failed
    doc_id: Optional[str] = None
    heading_id: Optional[str] = None
    revision_id: Optional[str] = None

@dataclasses.dataclass
class ReceiptDeliveryGmail:
    status: str = "pending" # pending, drafted, sent, failed
    draft_id: Optional[str] = None
    message_id: Optional[str] = None

@dataclasses.dataclass
class ReceiptDelivery:
    google_doc: ReceiptDeliveryDocs = dataclasses.field(default_factory=ReceiptDeliveryDocs)
    gmail: ReceiptDeliveryGmail = dataclasses.field(default_factory=ReceiptDeliveryGmail)

@dataclasses.dataclass
class RunReceipt:
    idempotency_key: str
    run_timestamp: str
    review_window: Dict[str, str]
    reviews_ingested: int
    clusters_found: int
    themes_generated: int
    delivery: ReceiptDelivery = dataclasses.field(default_factory=ReceiptDelivery)
    llm_usage: Dict[str, Any] = dataclasses.field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        return dataclasses.asdict(self)
        
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "RunReceipt":
        docs_data = data.get("delivery", {}).get("google_doc", {})
        gmail_data = data.get("delivery", {}).get("gmail", {})
        
        delivery = ReceiptDelivery(
            google_doc=ReceiptDeliveryDocs(**docs_data),
            gmail=ReceiptDeliveryGmail(**gmail_data)
        )
        
        return cls(
            idempotency_key=data["idempotency_key"],
            run_timestamp=data["run_timestamp"],
            review_window=data.get("review_window", {}),
            reviews_ingested=data.get("reviews_ingested", 0),
            clusters_found=data.get("clusters_found", 0),
            themes_generated=data.get("themes_generated", 0),
            delivery=delivery,
            llm_usage=data.get("llm_usage", {})
        )

def get_receipt_path(storage_path: str, iso_week: str) -> Path:
    return Path(storage_path) / f"groww_{iso_week}.json"

def load_receipt(storage_path: str, iso_week: str) -> Optional[RunReceipt]:
    path = get_receipt_path(storage_path, iso_week)
    if not path.exists():
        return None
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
            return RunReceipt.from_dict(data)
    except Exception:
        return None

def save_receipt(storage_path: str, iso_week: str, receipt: RunReceipt) -> None:
    path = get_receipt_path(storage_path, iso_week)
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(receipt.to_dict(), f, indent=2)
