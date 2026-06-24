"""Groww Pulse — Review ingestion from Play Store MCP server."""

import asyncio
import json
import logging
from datetime import datetime, timedelta, timezone
from typing import List

from mcp.client.stdio import stdio_client, StdioServerParameters
from mcp.client.session import ClientSession

from groww_pulse.config import Config
from groww_pulse.pii import scrub_text
from mcp_servers.playstore_reviews.scraper import Review


import sys

async def fetch_from_mcp(config: Config) -> List[Review]:
    """Connect to Play Store MCP and fetch raw reviews."""
    server_params = StdioServerParameters(
        command=sys.executable,
        args=["-m", "mcp_servers.playstore_reviews"],
        env=None
    )
    
    logging.info(f"Connecting to MCP server for app {config.product.play_store_app_id}...")
    try:
        async with stdio_client(server_params) as (read, write):
            async with ClientSession(read, write) as session:
                await session.initialize()
                
                # The MCP server might return text content.
                result = await session.call_tool(
                    "fetch_reviews",
                    arguments={
                        "app_id": config.product.play_store_app_id,
                        "count": config.ingestion.max_reviews,
                        "lang": "en",
                        "sort": "newest"
                    }
                )
                
                if result.isError:
                    raise RuntimeError(f"MCP tool error: {result.content}")
                    
                # FastMCP serializes a list of dicts into multiple TextContent objects
                raw_reviews = []
                for c in result.content:
                    parsed = json.loads(c.text)
                    if isinstance(parsed, str):
                        parsed = json.loads(parsed)
                    raw_reviews.append(parsed)
                
                # Convert dicts back to Review objects
                return [
                    Review(
                        review_id=r["review_id"],
                        author=r["author"],
                        rating=r["rating"],
                        text=r["text"],
                        timestamp=r["timestamp"],
                        thumbs_up=r["thumbs_up"],
                        app_version=r.get("app_version")
                    )
                    for r in raw_reviews
                ]
    except Exception as e:
        logging.error(f"Failed to fetch from MCP: {e}")
        raise


def filter_by_date(reviews: List[Review], window_weeks: int) -> List[Review]:
    """Drop reviews outside the window."""
    now = datetime.now(timezone.utc)
    cutoff = now - timedelta(weeks=window_weeks)
    
    filtered = []
    for r in reviews:
        try:
            # Parse ISO timestamp
            dt = datetime.fromisoformat(r.timestamp.replace('Z', '+00:00'))
            # Ensure timezone awareness
            if dt.tzinfo is None:
                dt = dt.replace(tzinfo=timezone.utc)
                
            if dt >= cutoff:
                filtered.append(r)
        except ValueError:
            logging.warning(f"Could not parse timestamp {r.timestamp} for review {r.review_id}")
            # If timestamp is invalid, we still keep it (or drop, but keeping is safer)
            filtered.append(r)
            
    logging.info(f"Filtered {len(reviews)} reviews to {len(filtered)} within {window_weeks}-week window")
    return filtered


def scrub_pii(reviews: List[Review]) -> List[Review]:
    """Scrub PII from author and text fields."""
    total_redactions = 0
    for r in reviews:
        r.text, txt_redactions = scrub_text(r.text)
        r.author, auth_redactions = scrub_text(r.author)
        total_redactions += txt_redactions + auth_redactions
        
    logging.info(f"Scrubbed {total_redactions} PII instances across {len(reviews)} reviews")
    return reviews


def deduplicate(reviews: List[Review]) -> List[Review]:
    """Deduplicate reviews by review_id."""
    seen = set()
    deduped = []
    for r in reviews:
        if r.review_id not in seen:
            seen.add(r.review_id)
            deduped.append(r)
            
    logging.info(f"Deduplication: {len(reviews)} -> {len(deduped)}")
    return deduped


async def ingest_reviews(config: Config) -> List[Review]:
    """End-to-end ingestion pipeline."""
    # 1. Fetch
    reviews = await fetch_from_mcp(config)
    
    # 2. Filter by date
    reviews = filter_by_date(reviews, config.ingestion.window_weeks)
    
    # 3. Deduplicate
    reviews = deduplicate(reviews)
    
    # 4. Scrub PII
    reviews = scrub_pii(reviews)
    
    return reviews
