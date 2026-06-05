import logging
import os
import random
import requests
from typing import Optional

logger = logging.getLogger(__name__)

_BASE_URL = "https://api.unsplash.com"

# How many results to fetch and randomly pick from.
# Prevents every article on the same topic getting the identical photo.
_POOL_SIZE = 10


def _optimized_url(raw_url: str, width: int = 800, height: int = 420, quality: int = 72) -> str:
    """
    Convert any Unsplash photo URL to a stable, size-controlled URL.
    Uses the raw base URL + explicit crop params so images stay fast and
    consistent even if Unsplash rotates their ixlib version.
    """
    # Strip existing query string; work from the raw base
    base = raw_url.split("?")[0]
    return f"{base}?w={width}&h={height}&fit=crop&q={quality}&auto=format&fm=webp"


def fetch_image(search_term: str) -> Optional[dict]:
    """
    Fetch a relevant image from Unsplash API.

    Returns dict with: url, photographer, attribution_link, alt_text
    Returns None if fetch fails or Unsplash API key not configured.
    """
    access_key = os.getenv("UNSPLASH_ACCESS_KEY")
    if not access_key:
        logger.debug("UNSPLASH_ACCESS_KEY not set — skipping image fetch")
        return None

    try:
        params = {
            "query": search_term,
            "per_page": _POOL_SIZE,
            "orientation": "landscape",
            "client_id": access_key,
        }

        resp = requests.get(f"{_BASE_URL}/search/photos", params=params, timeout=10)
        resp.raise_for_status()

        data = resp.json()
        results = data.get("results", [])
        if not results:
            logger.warning(f"No images found for: {search_term}")
            return None

        # Pick a random photo from the pool so similar articles get different images
        photo = random.choice(results)

        raw_url = photo["urls"].get("raw") or photo["urls"]["full"]
        optimized = _optimized_url(raw_url)

        return {
            "url": optimized,
            "photographer": photo.get("user", {}).get("name", "Unknown"),
            "attribution_link": photo["links"]["html"],
            "alt_text": photo.get("alt_description") or search_term,
        }
    except Exception as e:
        logger.error(f"Unsplash fetch failed for '{search_term}': {e}")
        return None
