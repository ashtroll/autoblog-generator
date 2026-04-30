import time
import logging
from typing import List, Dict

logger = logging.getLogger(__name__)


def fetch(country: str = "india") -> List[Dict]:
    try:
        from pytrends.request import TrendReq
        pytrends = TrendReq(hl="en-US", tz=330)
        time.sleep(2)
        df = pytrends.trending_searches(pn=country)
        topics = []
        for title in df[0].head(15).tolist():
            topics.append({
                "title": title,
                "description": f"Trending search on Google: {title}",
                "source_urls": [],
                "source": "google_trends",
                "fetched_at": time.time(),
            })
        logger.info(f"Google Trends: fetched {len(topics)} topics")
        return topics
    except Exception as e:
        logger.warning(f"Google Trends fetch failed: {e}")
        return []
