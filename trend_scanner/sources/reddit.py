import time
import logging
import requests
from typing import List, Dict

logger = logging.getLogger(__name__)

_SUBREDDITS = [
    "technology", "worldnews", "science", "business",
    "news", "india", "finance", "space", "health", "environment",
]
_HEADERS = {"User-Agent": "AutoBlogBot/1.0"}


def fetch(limit: int = 15) -> List[Dict]:
    topics = []
    for sub in _SUBREDDITS:
        try:
            url = f"https://www.reddit.com/r/{sub}/hot.json?limit={limit}"
            resp = requests.get(url, headers=_HEADERS, timeout=10)
            resp.raise_for_status()
            posts = resp.json()["data"]["children"]
            for post in posts:
                data = post["data"]
                if data.get("stickied") or data.get("is_self") is False and not data.get("url"):
                    continue
                title = data.get("title", "").strip()
                if not title:
                    continue
                topics.append({
                    "title": title,
                    "description": data.get("selftext", title)[:300] or title,
                    "source_urls": [f"https://reddit.com{data.get('permalink', '')}"],
                    "source": "reddit",
                    "fetched_at": time.time(),
                    "score": data.get("score", 0),
                })
            time.sleep(1)
        except Exception as e:
            logger.warning(f"Reddit fetch failed for r/{sub}: {e}")
    logger.info(f"Reddit: fetched {len(topics)} topics")
    return topics
