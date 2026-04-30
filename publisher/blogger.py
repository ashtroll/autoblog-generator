import logging
import os
import requests
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request

from blog_generator.models import BlogPost
from publisher.base import BasePublisher
from publisher.markdown_to_html import to_html

logger = logging.getLogger(__name__)

_API = "https://www.googleapis.com/blogger/v3/blogs/{blog_id}/posts/"


class BloggerPublisher(BasePublisher):
    def __init__(
        self,
        blog_id: str,
        client_id: str,
        client_secret: str,
        refresh_token: str,
        published: bool = False,
    ):
        self._blog_id = blog_id
        self._client_id = client_id
        self._client_secret = client_secret
        self._refresh_token = refresh_token
        self._published = published

    @classmethod
    def from_config(cls) -> "BloggerPublisher":
        return cls(
            blog_id=os.environ["BLOGGER_BLOG_ID"],
            client_id=os.environ["GOOGLE_CLIENT_ID"],
            client_secret=os.environ["GOOGLE_CLIENT_SECRET"],
            refresh_token=os.environ["GOOGLE_REFRESH_TOKEN"],
            published=os.getenv("BLOGGER_PUBLISHED", "false").lower() == "true",
        )

    def _get_access_token(self) -> str:
        creds = Credentials(
            token=None,
            refresh_token=self._refresh_token,
            token_uri="https://oauth2.googleapis.com/token",
            client_id=self._client_id,
            client_secret=self._client_secret,
        )
        creds.refresh(Request())
        return creds.token

    def publish(self, blog: BlogPost) -> dict:
        access_token = self._get_access_token()

        post_data = {
            "title": blog.title,
            "content": to_html(blog.content_md),
            "labels": blog.meta.tags,
        }

        params = {"isDraft": not self._published}

        response = requests.post(
            _API.format(blog_id=self._blog_id),
            json=post_data,
            params=params,
            headers={
                "Authorization": f"Bearer {access_token}",
                "Content-Type": "application/json",
            },
            timeout=30,
        )
        response.raise_for_status()
        data = response.json()
        logger.info(f"Blogger: posted '{blog.title}' → {data.get('url')}")
        return data
