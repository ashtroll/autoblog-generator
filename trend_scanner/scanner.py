import logging
import os
import re
from typing import List

from .sources import google_trends, newsapi_source, hackernews, googlenews, reddit
from .deduplicator import deduplicate
from .ranker import rank
from blog_generator.models import Topic

logger = logging.getLogger(__name__)
_GENERIC_TOPIC_WORDS = {
    "a",
    "an",
    "and",
    "article",
    "articles",
    "blog",
    "blogs",
    "breaking",
    "buzz",
    "coverage",
    "headline",
    "headlines",
    "latest",
    "live",
    "news",
    "post",
    "posts",
    "report",
    "reports",
    "story",
    "stories",
    "today",
    "topic",
    "topics",
    "trending",
    "update",
    "updates",
    "video",
    "videos",
    "watch",
}


def _is_low_quality_topic(title: str) -> bool:
    words = re.findall(r"[a-z0-9']+", title.lower())
    if len(words) < 4:
        return True
    if not words:
        return True
    generic_count = sum(1 for word in words if word in _GENERIC_TOPIC_WORDS)
    return generic_count / len(words) >= 0.75


class TrendScanner:
    def __init__(self, country: str = "india"):
        self.country = country

    def get_top_topics(self, count: int = 5) -> List[Topic]:
        raw: list = []

        raw.extend(google_trends.fetch(self.country))
        raw.extend(newsapi_source.fetch(os.getenv("NEWSAPI_KEY")))
        raw.extend(hackernews.fetch(limit=15))
        raw.extend(googlenews.fetch())
        raw.extend(reddit.fetch())

        logger.info(f"Scanner: collected {len(raw)} raw items from all sources")

        deduped = deduplicate(raw)
        top = rank(deduped, top_n=count)

        topics = []
        for item in top:
            title = item["title"].strip()
            if _is_low_quality_topic(title):
                logger.info(f"Skipping low-quality topic: {title}")
                continue
            topics.append(Topic(
                title=title,
                description=item.get("description", title),
                source_urls=item.get("source_urls", []),
                score=item.get("_rank_score", 0.0),
            ))
        return topics
