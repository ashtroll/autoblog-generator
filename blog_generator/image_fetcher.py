import logging
import os
import requests
from typing import Optional

logger = logging.getLogger(__name__)

_BASE_URL = "https://api.unsplash.com"


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
            "per_page": 1,
            "orientation": "landscape",
            "client_id": access_key,
        }

        resp = requests.get(f"{_BASE_URL}/search/photos", params=params, timeout=10)
        resp.raise_for_status()

        data = resp.json()
        if not data.get("results"):
            logger.warning(f"No images found for: {search_term}")
            return None

        photo = data["results"][0]
        return {
            "url": photo["urls"]["regular"],
            "photographer": photo.get("user", {}).get("name", "Unknown"),
            "attribution_link": photo["links"]["html"],
            "alt_text": photo.get("alt_description", search_term),
        }
    except Exception as e:
        logger.error(f"Unsplash fetch failed for '{search_term}': {e}")
        return None
