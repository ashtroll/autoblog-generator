import time
import logging
import os
from typing import List, Dict

logger = logging.getLogger(__name__)


def fetch(api_key: str | None = None) -> List[Dict]:
    try:
        from newsapi import NewsApiClient
        key = api_key or os.environ["NEWSAPI_KEY"]
        client = NewsApiClient(api_key=key)
        result = client.get_top_headlines(language="en", page_size=15)
        topics = []
        for article in result.get("articles", []):
            title = article.get("title") or ""
            if not title or title == "[Removed]":
                continue
            topics.append({
                "title": title,
                "description": article.get("description") or title,
                "source_urls": [article["url"]] if article.get("url") else [],
                "source": "newsapi",
                "fetched_at": time.time(),
            })
        logger.info(f"NewsAPI: fetched {len(topics)} topics")
        return topics
    except Exception as e:
        logger.warning(f"NewsAPI fetch failed: {e}")
        return []
