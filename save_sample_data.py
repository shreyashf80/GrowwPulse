import asyncio
import json
import os
from groww_pulse.ingestion import ingest_reviews
from groww_pulse.config import load_config
import dataclasses

async def save_ingested_data():
    config = load_config()
    # Set parameters for the 10-week full cache extraction
    config.ingestion.window_weeks = 10
    config.ingestion.max_reviews = 2000  # High enough to get the entire cache within 10 weeks
    
    print("Fetching and cleaning reviews... This may take a moment.")
    reviews = await ingest_reviews(config)
    print(f"Successfully processed {len(reviews)} clean reviews.")
    
    # Ensure data directory exists
    os.makedirs("data", exist_ok=True)
    
    # 1. Save actual reviews
    actual_output_path = "data/actual_reviews.json"
    with open(actual_output_path, "w", encoding="utf-8") as f:
        # Convert dataclasses to dict for JSON serialization
        reviews_dict = [dataclasses.asdict(r) for r in reviews]
        json.dump(reviews_dict, f, indent=2)
        
    print(f"Actual reviews saved to {actual_output_path}")

    # 2. Save normalized reviews (remove review_id, author, timestamp)
    normalized_output_path = "data/normalized_reviews.json"
    with open(normalized_output_path, "w", encoding="utf-8") as f:
        normalized_reviews = []
        for r in reviews_dict:
            norm_r = dict(r)
            norm_r.pop("review_id", None)
            norm_r.pop("author", None)
            norm_r.pop("timestamp", None)
            normalized_reviews.append(norm_r)
        
        json.dump(normalized_reviews, f, indent=2)

    print(f"Normalized reviews saved to {normalized_output_path}")

if __name__ == "__main__":
    asyncio.run(save_ingested_data())
