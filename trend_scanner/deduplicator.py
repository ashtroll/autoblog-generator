import re
import logging
from typing import List, Dict

logger = logging.getLogger(__name__)

_THRESHOLD = 70


def _normalize(text: str) -> str:
    text = text.lower()
    text = re.sub(r"[^\w\s]", "", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def deduplicate(topics: List[Dict]) -> List[Dict]:
    from rapidfuzz import fuzz

    seen: List[Dict] = []

    for topic in topics:
        norm = _normalize(topic["title"])
        is_dup = False
        for existing in seen:
            score = fuzz.partial_ratio(norm, _normalize(existing["title"]))
            if score >= _THRESHOLD:
                # Merge source_urls and keep the entry with the higher engagement score
                existing["source_urls"] = list(
                    set(existing.get("source_urls", []) + topic.get("source_urls", []))
                )
                existing["_source_count"] = existing.get("_source_count", 1) + 1
                is_dup = True
                break
        if not is_dup:
            merged = dict(topic)
            merged["_source_count"] = 1
            seen.append(merged)

    logger.info(f"Deduplication: {len(topics)} → {len(seen)} unique topics")
    return seen
