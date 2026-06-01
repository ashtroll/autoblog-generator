import time
import logging
from typing import List, Dict

import feedparser

logger = logging.getLogger(__name__)

_RSS_URL = "https://trends.google.com/trending/rss?geo=IN"


def fetch(country: str = "india") -> List[Dict]:
    try:
        feed = feedparser.parse(_RSS_URL)
        topics = []
        for entry in feed.entries[:15]:
            title = entry.get("title", "").strip()
            if not title:
                continue
            topics.append({
                "title": title,
                "description": entry.get("summary", f"Trending on Google: {title}"),
                "source_urls": [entry.get("link", "")] if entry.get("link") else [],
                "source": "google_trends_rss",
                "fetched_at": time.time(),
            })
        logger.info(f"Google Trends RSS: fetched {len(topics)} topics")
        return topics
    except Exception as e:
        logger.warning(f"Google Trends RSS fetch failed: {e}")
        return []
