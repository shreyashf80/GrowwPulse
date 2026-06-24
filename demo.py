import json
from groww_pulse.config import Config, ProductConfig, IngestionConfig, ClusteringConfig, LLMConfig, DeliveryConfig, ReceiptsConfig
from groww_pulse.renderer import render_docs_payload, render_email_payload

def run_demo():
    config = Config(
        product=ProductConfig(name="Groww", play_store_app_id="com.nextbillion.groww"),
        ingestion=IngestionConfig(window_weeks=12, max_reviews=2000),
        clustering=ClusteringConfig(umap_n_components=5, umap_n_neighbors=15, hdbscan_min_cluster_size=10, hdbscan_min_samples=5),
        llm=LLMConfig(model="llama-3.3-70b-versatile", temperature=0.2, max_tokens=100000, quote_validation=True),
        delivery=DeliveryConfig(google_doc_id="1a2b3c4d5e", email_recipients=[], draft_only=False),
        receipts=ReceiptsConfig(storage_path="data/receipts/")
    )

    themes = [
        {
            "theme_name": "Investment Features",
            "review_count": 184,
            "avg_rating": 4.84,
            "description": "Users praise the app for its ease of use and investment features.",
            "quotes": [
                {"text": "very good app for investment i love it", "rating": 5},
                {"text": "A very good app from an investment point of view", "rating": 5}
            ],
            "action_ideas": [
                {"title": "Enhance Investment Features", "detail": "Continuously update and expand the investment options."},
            ]
        },
        {
            "theme_name": "Glitches and Support",
            "review_count": 146,
            "avg_rating": 1.58,
            "description": "Users are experiencing technical issues and poor customer support.",
            "quotes": [
                {"text": "So many glitches, execution problem", "rating": 1},
                {"text": "Multiple Discrepancies, lags while doing Transactions", "rating": 1}
            ],
            "action_ideas": [
                {"title": "Improve App Stability", "detail": "Conduct thorough testing and debugging."}
            ]
        }
    ]

    print("\n--- Phase 4.1 Docs Payload (Plain Text) ---")
    docs_payload = render_docs_payload(themes, "2026-W24", config)
    print(docs_payload)

    print("\n--- Phase 4.2 Email Payload (HTML) ---")
    email_payload = render_email_payload(themes, "2026-W24", config, config.delivery.google_doc_id)
    print(email_payload.html_body)

if __name__ == "__main__":
    run_demo()
