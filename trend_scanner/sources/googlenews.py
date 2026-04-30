import time
import logging
import requests
import feedparser
from typing import List, Dict

logger = logging.getLogger(__name__)

_FEEDS = [
    "https://news.google.com/rss?hl=en-IN&gl=IN&ceid=IN:en",                                                                                                                      # Top stories India
    "https://news.google.com/rss?hl=en-US&gl=US&ceid=US:en",                                                                                                                      # Top stories US
    "https://news.google.com/rss/topics/CAAqJggKIiBDQkFTRWdvSUwyMHZNRGRqTVhZU0FtVnVHZ0pKVGlnQVAB?hl=en-IN&gl=IN&ceid=IN:en",  # Technology
    "https://news.google.com/rss/topics/CAAqJggKIiBDQkFTRWdvSUwyMHZNRGt3TVhZU0FtVnVHZ0pKVGlnQVAB?hl=en-IN&gl=IN&ceid=IN:en",  # Science
    "https://news.google.com/rss/topics/CAAqJggKIiBDQkFTRWdvSUwyMHZNREp5ZVhRU0FtVnVHZ0pKVGlnQVAB?hl=en-IN&gl=IN&ceid=IN:en",  # Business
    "https://news.google.com/rss/topics/CAAqIQgKIhtDQkFTRGdvSUwyMHZNR3QwTlRFU0FtVnVLQUFQAQ?hl=en-IN&gl=IN&ceid=IN:en",        # World
]


def fetch() -> List[Dict]:
    topics = []
    seen = set()
    for feed_url in _FEEDS:
        try:
            feed = feedparser.parse(feed_url)
            for entry in feed.entries[:12]:
                title = entry.get("title", "").strip()
                if not title or title in seen:
                    continue
                seen.add(title)
                topics.append({
                    "title": title,
                    "description": entry.get("summary", title)[:300],
                    "source_urls": [entry.get("link", "")],
                    "source": "google_news_rss",
                    "fetched_at": time.time(),
                })
        except Exception as e:
            logger.warning(f"Google News RSS fetch failed for {feed_url}: {e}")
    logger.info(f"Google News RSS: fetched {len(topics)} topics")
    return topics
