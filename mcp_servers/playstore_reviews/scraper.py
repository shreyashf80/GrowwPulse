"""Play Store Reviews MCP Server — Google Play scraping logic."""

import re
from dataclasses import dataclass
from typing import List, Optional, Any

from google_play_scraper import reviews as fetch_google_reviews, Sort
import emoji
from langdetect import detect, DetectorFactory
from langdetect.lang_detect_exception import LangDetectException

# To ensure consistent language detection results
DetectorFactory.seed = 0

@dataclass
class Review:
    review_id: str
    author: str
    rating: int          # 1–5
    text: str
    timestamp: str       # ISO-8601
    thumbs_up: int
    app_version: Optional[str]

def _is_valid_review(text: str) -> bool:
    """Check if the review matches the filter criteria:
    - >= 8 words
    - No emojis
    - English language
    """
    if not text:
        return False
        
    text_str = str(text).strip()
    
    # 1. Check >= 8 words
    words = text_str.split()
    if len(words) < 8:
        return False
        
    # 2. Check no emojis
    if emoji.emoji_count(text_str) > 0:
        return False
        
    # 3. Check English language
    try:
        if detect(text_str) != 'en':
            return False
    except LangDetectException:
        return False
        
    return True

def fetch_reviews_with_filters(app_id: str, lang: str = "en", count: int = 1000, sort_order: str = "newest") -> List[Review]:
    """Fetch reviews from Google Play Store with applied filters."""
    
    sort_mapping = {
        "newest": Sort.NEWEST,
        "rating": Sort.RATING,
        "most_relevant": Sort.MOST_RELEVANT
    }
    
    actual_sort = sort_mapping.get(sort_order, Sort.NEWEST)
    
    collected_reviews: List[Review] = []
    continuation_token = None
    
    # Fetch in chunks to avoid fetching too many if filters reject most
    chunk_size = 200
    if count < chunk_size:
        chunk_size = count
        
    # Limit maximum iterations to avoid infinite loops if it's hard to find matching reviews
    max_fetches = max(20, (count // chunk_size) * 5)
    fetches = 0
    
    while len(collected_reviews) < count and fetches < max_fetches:
        result, continuation_token = fetch_google_reviews(
            app_id,
            lang=lang, # Default to requesting English
            country='us', # Can be param if needed
            sort=actual_sort,
            count=chunk_size,
            continuation_token=continuation_token
        )
        fetches += 1
        
        for r in result:
            if len(collected_reviews) >= count:
                break
                
            text = r.get("content", "")
            if _is_valid_review(text):
                # Map to schema
                review = Review(
                    review_id=r.get("reviewId", ""),
                    author=r.get("userName", ""),
                    rating=r.get("score", 0),
                    text=text,
                    timestamp=r.get("at", "").isoformat() if hasattr(r.get("at", ""), "isoformat") else str(r.get("at", "")),
                    thumbs_up=r.get("thumbsUpCount", 0),
                    app_version=r.get("reviewCreatedVersion")
                )
                collected_reviews.append(review)
                
        if not continuation_token:
            break
            
    return collected_reviews
