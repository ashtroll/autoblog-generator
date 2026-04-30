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
            "content": self._build_content(blog),
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
        logger.info(f"Blogger: posted '{blog.title}' -> {data.get('url')}")
        return data

    def _build_content(self, blog: BlogPost) -> str:
        body_html = to_html(blog.content_md)
        tags_html = " ".join(
            f'<a href="/search/label/{t}" rel="tag">{t}</a>'
            for t in blog.meta.tags
        )
        schema = f"""
<script type="application/ld+json">
{{
  "@context": "https://schema.org",
  "@type": "BlogPosting",
  "headline": "{blog.title.replace('"', '&quot;')}",
  "description": "{blog.meta.meta_description.replace('"', '&quot;')}",
  "datePublished": "{__import__('datetime').datetime.utcnow().isoformat()}Z",
  "author": {{"@type": "Organization", "name": "TinkerStack"}},
  "publisher": {{
    "@type": "Organization",
    "name": "TinkerStack",
    "url": "https://tinkerstackk.blogspot.com"
  }},
  "keywords": "{', '.join(blog.meta.tags)}"
}}
</script>"""

        read_time = blog.meta.estimated_read_time
        return f"""
{schema}
<div class="post-meta-bar" style="display:flex;gap:16px;align-items:center;
  padding:12px 0 20px;border-bottom:1px solid #e2e8f0;margin-bottom:28px;
  color:#64748b;font-size:0.85rem;font-family:Inter,sans-serif;">
  <span>&#128337; {read_time}</span>
  <span>&#127991; {tags_html}</span>
</div>
{body_html}
<div class="post-footer-cta" style="background:linear-gradient(135deg,#eff6ff,#dbeafe);
  border:1px solid #bfdbfe;border-radius:12px;padding:24px;margin-top:40px;
  text-align:center;font-family:Inter,sans-serif;">
  <p style="font-weight:700;font-size:1.05rem;color:#1e3a8a;margin-bottom:8px;">
    Found this useful? Share it.</p>
  <p style="color:#3b82f6;font-size:0.9rem;margin:0;">
    Follow TinkerStack for daily insights on tech, science, and the world.</p>
</div>"""
