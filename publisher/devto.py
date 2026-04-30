import logging
import os
import requests

from blog_generator.models import BlogPost
from .base import BasePublisher

logger = logging.getLogger(__name__)

_API = "https://dev.to/api/articles"


class DevToPublisher(BasePublisher):
    def __init__(self, api_key: str, published: bool = False):
        self._api_key = api_key
        self._published = published

    @classmethod
    def from_config(cls) -> "DevToPublisher":
        return cls(
            api_key=os.environ["DEVTO_API_KEY"],
            published=os.getenv("DEVTO_PUBLISHED", "false").lower() == "true",
        )

    def publish(self, blog: BlogPost) -> dict:
        # Dev.to: max 4 tags, lowercase, no spaces
        tags = [t.lower().replace(" ", "-") for t in blog.meta.tags[:4]]

        payload = {
            "article": {
                "title": blog.title,
                "body_markdown": blog.content_md,
                "published": self._published,
                "description": blog.meta.meta_description,
                "tags": tags,
            }
        }

        response = requests.post(
            _API,
            json=payload,
            headers={"api-key": self._api_key},
            timeout=30,
        )
        response.raise_for_status()
        data = response.json()
        logger.info(f"Dev.to: posted '{blog.title}' → {data.get('url')}")
        return data
