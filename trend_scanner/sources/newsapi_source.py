import time
import logging
import os
from typing import List, Dict

logger = logging.getLogger(__name__)


_CATEGORIES = ["general", "technology", "science", "business", "health", "entertainment"]


def fetch(api_key: str | None = None) -> List[Dict]:
    try:
        from newsapi import NewsApiClient
        key = api_key or os.environ["NEWSAPI_KEY"]
        client = NewsApiClient(api_key=key)
        topics = []
        seen = set()
        for category in _CATEGORIES:
            try:
                result = client.get_top_headlines(language="en", category=category, page_size=10)
                for article in result.get("articles", []):
                    title = article.get("title") or ""
                    if not title or title == "[Removed]" or title in seen:
                        continue
                    seen.add(title)
                    topics.append({
                        "title": title,
                        "description": article.get("description") or title,
                        "source_urls": [article["url"]] if article.get("url") else [],
                        "source": "newsapi",
                        "fetched_at": time.time(),
                    })
            except Exception as e:
                logger.warning(f"NewsAPI category '{category}' failed: {e}")
        logger.info(f"NewsAPI: fetched {len(topics)} topics across {len(_CATEGORIES)} categories")
        return topics
    except Exception as e:
        logger.warning(f"NewsAPI fetch failed: {e}")
        return []
