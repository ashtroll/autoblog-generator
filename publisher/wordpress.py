import logging
import os
import requests
from requests.auth import HTTPBasicAuth

from blog_generator.models import BlogPost
from .base import BasePublisher

logger = logging.getLogger(__name__)


class WordPressPublisher(BasePublisher):
    def __init__(self, site_url: str, username: str, app_password: str, status: str = "draft"):
        self._api = f"{site_url.rstrip('/')}/wp-json/wp/v2"
        self._auth = HTTPBasicAuth(username, app_password)
        self._status = status

    @classmethod
    def from_config(cls) -> "WordPressPublisher":
        return cls(
            site_url=os.environ["WP_URL"],
            username=os.environ["WP_USER"],
            app_password=os.environ["WP_APP_PASSWORD"],
            status=os.getenv("WP_POST_STATUS", "draft"),
        )

    def publish(self, blog: BlogPost) -> dict:
        tag_ids = self._get_or_create_tags(blog.meta.tags)
        post_data = {
            "title": blog.title,
            "content": blog.content_html,
            "status": self._status,
            "slug": blog.meta.slug,
            "excerpt": blog.meta.meta_description,
            "tags": tag_ids,
        }
        response = requests.post(
            f"{self._api}/posts",
            json=post_data,
            auth=self._auth,
            timeout=30,
        )
        response.raise_for_status()
        data = response.json()
        logger.info(f"WordPress: published '{blog.title}' → {data.get('link')}")
        return data

    def _get_or_create_tags(self, tag_names: list[str]) -> list[int]:
        ids = []
        for name in tag_names:
            tag_id = self._find_tag(name)
            if tag_id is None:
                tag_id = self._create_tag(name)
            if tag_id is not None:
                ids.append(tag_id)
        return ids

    def _find_tag(self, name: str) -> int | None:
        resp = requests.get(
            f"{self._api}/tags",
            params={"search": name, "per_page": 5},
            auth=self._auth,
            timeout=10,
        )
        if resp.ok:
            for tag in resp.json():
                if tag["name"].lower() == name.lower():
                    return tag["id"]
        return None

    def _create_tag(self, name: str) -> int | None:
        resp = requests.post(
            f"{self._api}/tags",
            json={"name": name},
            auth=self._auth,
            timeout=10,
        )
        if resp.ok:
            return resp.json().get("id")
        logger.warning(f"WordPress: could not create tag '{name}': {resp.text[:200]}")
        return None
