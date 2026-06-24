"""Play Store Reviews MCP Server — tool definitions."""

import logging
from typing import List, Dict, Any

from mcp.server.fastmcp import FastMCP
from mcp_servers.playstore_reviews.scraper import fetch_reviews_with_filters

# Initialize FastMCP server
mcp = FastMCP("Play Store Reviews")

@mcp.tool()
def fetch_reviews(app_id: str = "com.nextbillion.groww", lang: str = "en", count: int = 1000, sort: str = "newest") -> List[Dict[str, Any]]:
    """Fetch structured Groww review data from Google Play.
    
    Filters out:
    - Reviews with less than 8 words
    - Reviews containing emojis
    - Non-English reviews
    """
    
    try:
        reviews = fetch_reviews_with_filters(app_id=app_id, lang=lang, count=count, sort_order=sort)
        # Return as dicts for serialization
        return [
            {
                "review_id": r.review_id,
                "author": r.author,
                "rating": r.rating,
                "text": r.text,
                "timestamp": r.timestamp,
                "thumbs_up": r.thumbs_up,
                "app_version": r.app_version
            }
            for r in reviews
        ]
    except Exception as e:
        logging.error(f"Failed to fetch reviews: {e}")
        raise ValueError(f"Failed to fetch reviews from Google Play Store: {e}")
