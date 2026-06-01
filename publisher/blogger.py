import logging
import os
import datetime
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
        body_html = to_html(
            blog.content_md,
            featured_image_url=blog.featured_image_url,
            featured_image_credit=blog.featured_image_credit,
        )

        category = (blog.meta.tags[0] if blog.meta.tags else "Latest").strip()
        read_time = blog.meta.estimated_read_time or "5 min read"
        dek = blog.meta.meta_description or ""
        labels_attr = ",".join(blog.meta.tags[:8])

        schema = self._build_schema(blog)
        progress_bar = (
            '<div class="ts-progress" id="ts-progress" aria-hidden="true"></div>'
            '<script>'
            '(function(){var b=document.getElementById("ts-progress");if(!b)return;'
            'window.addEventListener("scroll",function(){'
            'var h=document.documentElement,s=h.scrollTop||document.body.scrollTop,'
            'm=(h.scrollHeight||document.body.scrollHeight)-h.clientHeight;'
            'b.style.width=(m>0?(s/m*100):0)+"%";});})();'
            '</script>'
        )

        article_header = (
            '<header class="ts-article-header">'
            f'<div class="ts-eyebrow">{category}</div>'
            f'<h1 class="ts-article-title">{self._esc(blog.title)}</h1>'
            f'<p class="ts-article-dek">{self._esc(dek)}</p>'
            '<div class="ts-article-byline">'
            'By <strong>TinkerStack</strong>'
            f' &middot; <span>{read_time}</span>'
            f' &middot; <time>{datetime.datetime.utcnow().strftime("%B %d, %Y")}</time>'
            '</div>'
            '</header>'
        )

        share_bar = (
            '<div class="ts-share-rail">'
            '<span class="ts-share-label">Share</span>'
            '<a class="ts-share-link" href="https://twitter.com/intent/tweet" rel="nofollow noopener" target="_blank">Twitter</a>'
            '<a class="ts-share-link" href="https://www.facebook.com/sharer/sharer.php" rel="nofollow noopener" target="_blank">Facebook</a>'
            '<a class="ts-share-link" href="https://api.whatsapp.com/send" rel="nofollow noopener" target="_blank">WhatsApp</a>'
            '<a class="ts-share-link" href="#" onclick="navigator.clipboard&amp;&amp;navigator.clipboard.writeText(location.href);return false;">Copy link</a>'
            '</div>'
        )

        related_mount = (
            f'<div class="ts-related-mount" data-labels="{self._esc(labels_attr)}"></div>'
        )

        footer_cta = (
            '<div class="ts-footer-cta">'
            '<h4>Get tomorrow\'s briefing in your inbox</h4>'
            '<p>Hand-picked stories from the world of technology, science, and business — every morning.</p>'
            '<a class="ts-footer-cta-link" href="/">Read more on TinkerStack &rarr;</a>'
            '</div>'
        )

        return (
            f'{schema}'
            f'{progress_bar}'
            '<article class="ts-article">'
            f'{article_header}'
            f'{body_html}'
            f'{share_bar}'
            f'{related_mount}'
            f'{footer_cta}'
            '</article>'
        )

    def _build_schema(self, blog: BlogPost) -> str:
        title = self._esc_json(blog.title)
        desc = self._esc_json(blog.meta.meta_description)
        keywords = self._esc_json(", ".join(blog.meta.tags))
        date_iso = datetime.datetime.utcnow().isoformat()
        image_block = ""
        if blog.featured_image_url:
            image_block = f'"image": "{blog.featured_image_url}",\n  '
        return (
            '<script type="application/ld+json">\n'
            '{\n'
            '  "@context": "https://schema.org",\n'
            '  "@type": "BlogPosting",\n'
            f'  "headline": "{title}",\n'
            f'  "description": "{desc}",\n'
            f'  {image_block}"datePublished": "{date_iso}Z",\n'
            '  "author": {"@type": "Organization", "name": "TinkerStack"},\n'
            '  "publisher": {\n'
            '    "@type": "Organization",\n'
            '    "name": "TinkerStack",\n'
            '    "url": "https://tinkerstackk.blogspot.com"\n'
            '  },\n'
            f'  "keywords": "{keywords}"\n'
            '}\n'
            '</script>'
        )

    @staticmethod
    def _esc(text: str) -> str:
        return (
            (text or "")
            .replace("&", "&amp;")
            .replace("<", "&lt;")
            .replace(">", "&gt;")
            .replace('"', "&quot;")
        )

    @staticmethod
    def _esc_json(text: str) -> str:
        return (text or "").replace("\\", "\\\\").replace('"', '\\"').replace("\n", " ")
