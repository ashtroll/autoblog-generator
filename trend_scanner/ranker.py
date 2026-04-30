import time
import logging
from typing import List, Dict

logger = logging.getLogger(__name__)

_MAX_AGE = 86400  # 24 hours


def _recency_weight(fetched_at: float) -> float:
    age = time.time() - fetched_at
    if age <= 3600:
        return 3.0
    if age <= 21600:
        return 2.0
    if age <= _MAX_AGE:
        return 1.0
    return 0.5


def _engagement(topic: Dict) -> float:
    hn_score = topic.get("score", 0)
    url_count = len(topic.get("source_urls", []))
    return min(hn_score / 100, 2.0) + min(url_count * 0.5, 1.0)


def rank(topics: List[Dict], top_n: int = 5) -> List[Dict]:
    for t in topics:
        source_count = t.get("_source_count", 1)
        recency = _recency_weight(t.get("fetched_at", time.time()))
        engagement = _engagement(t)
        t["_rank_score"] = source_count * 2 + recency + engagement

    ranked = sorted(topics, key=lambda t: t["_rank_score"], reverse=True)
    top = ranked[:top_n]
    logger.info(f"Ranker: returning top {len(top)} of {len(topics)} topics")
    return top
