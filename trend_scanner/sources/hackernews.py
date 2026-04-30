import time
import logging
import requests
from typing import List, Dict

logger = logging.getLogger(__name__)

_BASE = "https://hacker-news.firebaseio.com/v0"


def fetch(limit: int = 15) -> List[Dict]:
    try:
        ids = requests.get(f"{_BASE}/topstories.json", timeout=10).json()
        topics = []
        for story_id in ids[:limit]:
            try:
                story = requests.get(f"{_BASE}/item/{story_id}.json", timeout=5).json()
                title = story.get("title") or ""
                if not title:
                    continue
                topics.append({
                    "title": title,
                    "description": title,
                    "source_urls": [story["url"]] if story.get("url") else [],
                    "source": "hackernews",
                    "fetched_at": time.time(),
                    "score": story.get("score", 0),
                })
            except Exception:
                continue
        logger.info(f"HackerNews: fetched {len(topics)} topics")
        return topics
    except Exception as e:
        logger.warning(f"HackerNews fetch failed: {e}")
        return []
