import logging
import os
from typing import List

from .sources import google_trends, newsapi_source, hackernews
from .deduplicator import deduplicate
from .ranker import rank
from blog_generator.models import Topic

logger = logging.getLogger(__name__)


class TrendScanner:
    def __init__(self, country: str = "india"):
        self.country = country

    def get_top_topics(self, count: int = 5) -> List[Topic]:
        raw: list = []

        raw.extend(google_trends.fetch(self.country))
        raw.extend(newsapi_source.fetch(os.getenv("NEWSAPI_KEY")))
        raw.extend(hackernews.fetch(limit=15))

        logger.info(f"Scanner: collected {len(raw)} raw items from all sources")

        deduped = deduplicate(raw)
        top = rank(deduped, top_n=count)

        topics = []
        for item in top:
            topics.append(Topic(
                title=item["title"],
                description=item.get("description", item["title"]),
                source_urls=item.get("source_urls", []),
                score=item.get("_rank_score", 0.0),
            ))
        return topics
