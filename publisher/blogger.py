import logging
import os
import re
import datetime
import requests
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request

from blog_generator.models import BlogPost
from publisher.base import BasePublisher
from publisher.markdown_to_html import to_html

logger = logging.getLogger(__name__)

_API = "https://www.googleapis.com/blogger/v3/blogs/{blog_id}/posts/"
_SITE_URL = "https://tinkerstackk.blogspot.com"
_SITE_NAME = "TinkerStack"


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

        # Build content with a placeholder URL first; we'll update after we have the real URL
        post_data = {
            "title": blog.title,
            "content": self._build_content(blog, post_url=""),
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
        post_url = data.get("url", "")
        post_id = data.get("id", "")
        logger.info(f"Blogger: posted '{blog.title}' -> {post_url}")

        # Now patch the post with schema that includes the real URL
        if post_url and post_id:
            try:
                patched_content = self._build_content(blog, post_url=post_url)
                requests.patch(
                    _API.format(blog_id=self._blog_id) + post_id,
                    json={"content": patched_content},
                    headers={
                        "Authorization": f"Bearer {access_token}",
                        "Content-Type": "application/json",
                    },
                    timeout=30,
                )
                logger.info(f"Blogger: patched schema URL for '{blog.title}'")
            except Exception as e:
                logger.warning(f"Schema URL patch failed (non-critical): {e}")

        return data

    def _build_content(self, blog: BlogPost, post_url: str = "") -> str:
        body_html = to_html(
            blog.content_md,
            featured_image_url=blog.featured_image_url,
            featured_image_credit=blog.featured_image_credit,
            title=blog.title,
        )

        category = (blog.meta.tags[0] if blog.meta.tags else "Latest").strip()
        read_time = blog.meta.estimated_read_time or "5 min read"
        dek = blog.meta.meta_description or ""
        labels_attr = ",".join(blog.meta.tags[:8])
        date_str = datetime.datetime.utcnow().strftime("%B %d, %Y")
        date_iso = datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")

        schema = self._build_schema(blog, post_url=post_url)
        faq_schema = self._build_faq_schema(body_html)
        breadcrumb_schema = self._build_breadcrumb_schema(blog, post_url=post_url)
        og_meta = self._build_og_meta(blog, post_url=post_url)

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
            '<header class="ts-article-header" itemscope="" itemtype="https://schema.org/BlogPosting">'
            f'<div class="ts-eyebrow" itemprop="articleSection">{category}</div>'
            f'<h1 class="ts-article-title" itemprop="headline">{self._esc(blog.title)}</h1>'
            f'<p class="ts-article-dek" itemprop="description">{self._esc(dek)}</p>'
            '<div class="ts-article-byline">'
            'By <strong itemprop="author" itemscope="" itemtype="https://schema.org/Organization">'
            f'<span itemprop="name">{_SITE_NAME}</span></strong>'
            f' &middot; <span itemprop="timeRequired">{read_time}</span>'
            f' &middot; <time itemprop="datePublished" datetime="{date_iso}">{date_str}</time>'
            '</div>'
            '</header>'
        )

        # Share buttons with real URL injection via JS
        share_bar = (
            '<div class="ts-share-rail">'
            '<span class="ts-share-label">Share</span>'
            '<a class="ts-share-link ts-share-twitter" href="#" rel="nofollow noopener noreferrer" target="_blank">Twitter</a>'
            '<a class="ts-share-link ts-share-facebook" href="#" rel="nofollow noopener noreferrer" target="_blank">Facebook</a>'
            '<a class="ts-share-link ts-share-whatsapp" href="#" rel="nofollow noopener noreferrer" target="_blank">WhatsApp</a>'
            '<a class="ts-share-link ts-share-copy" href="#" onclick="navigator.clipboard&&navigator.clipboard.writeText(location.href);return false;">Copy link</a>'
            '</div>'
            '<script>'
            '(function(){'
            'var u=encodeURIComponent(location.href);'
            'var t=encodeURIComponent(document.title);'
            'var tw=document.querySelector(".ts-share-twitter");'
            'var fb=document.querySelector(".ts-share-facebook");'
            'var wa=document.querySelector(".ts-share-whatsapp");'
            'if(tw)tw.href="https://twitter.com/intent/tweet?url="+u+"&text="+t;'
            'if(fb)fb.href="https://www.facebook.com/sharer/sharer.php?u="+u;'
            'if(wa)wa.href="https://api.whatsapp.com/send?text="+t+"%20"+u;'
            '})();'
            '</script>'
        )

        related_mount = (
            f'<div class="ts-related-mount" data-labels="{self._esc(labels_attr)}"></div>'
        )

        footer_cta = (
            '<div class="ts-footer-cta">'
            f'<h4>Get tomorrow\'s briefing in your inbox</h4>'
            '<p>Hand-picked stories from the world of technology, science, and business — every morning.</p>'
            f'<a class="ts-footer-cta-link" href="{_SITE_URL}">Read more on {_SITE_NAME} &rarr;</a>'
            '</div>'
        )

        return (
            f'{og_meta}'
            f'{schema}'
            f'{faq_schema}'
            f'{breadcrumb_schema}'
            f'{progress_bar}'
            '<article class="ts-article" itemscope="" itemtype="https://schema.org/BlogPosting">'
            f'{article_header}'
            f'{body_html}'
            f'{share_bar}'
            f'{related_mount}'
            f'{footer_cta}'
            '</article>'
        )

    # -------------------------------------------------------------------------
    # Schema builders
    # -------------------------------------------------------------------------

    def _build_schema(self, blog: BlogPost, post_url: str = "") -> str:
        title = self._esc_json(blog.title)
        desc = self._esc_json(blog.meta.meta_description)
        keywords = self._esc_json(", ".join(blog.meta.tags))
        date_iso = datetime.datetime.utcnow().isoformat() + "Z"
        word_count = len((blog.content_md or "").split())
        read_time_mins = max(1, round(word_count / 250))
        article_section = self._esc_json(blog.meta.tags[0]) if blog.meta.tags else "Technology"
        url_val = self._esc_json(post_url) if post_url else _SITE_URL

        image_block = ""
        if blog.featured_image_url:
            image_block = (
                f'  "image": {{\n'
                f'    "@type": "ImageObject",\n'
                f'    "url": "{self._esc_json(blog.featured_image_url)}",\n'
                f'    "width": 1200,\n'
                f'    "height": 630\n'
                f'  }},\n'
            )

        return (
            '<script type="application/ld+json">\n'
            '{\n'
            '  "@context": "https://schema.org",\n'
            '  "@type": "BlogPosting",\n'
            f'  "headline": "{title}",\n'
            f'  "description": "{desc}",\n'
            f'  "url": "{url_val}",\n'
            f'{image_block}'
            f'  "datePublished": "{date_iso}",\n'
            f'  "dateModified": "{date_iso}",\n'
            f'  "wordCount": {word_count},\n'
            f'  "timeRequired": "PT{read_time_mins}M",\n'
            f'  "articleSection": "{article_section}",\n'
            '  "inLanguage": "en-US",\n'
            '  "mainEntityOfPage": {\n'
            '    "@type": "WebPage",\n'
            f'    "@id": "{url_val}"\n'
            '  },\n'
            '  "isPartOf": {\n'
            '    "@type": "Blog",\n'
            f'    "name": "{_SITE_NAME}",\n'
            f'    "url": "{_SITE_URL}"\n'
            '  },\n'
            '  "author": {\n'
            '    "@type": "Organization",\n'
            f'    "name": "{_SITE_NAME}",\n'
            f'    "url": "{_SITE_URL}"\n'
            '  },\n'
            '  "publisher": {\n'
            '    "@type": "Organization",\n'
            f'    "name": "{_SITE_NAME}",\n'
            f'    "url": "{_SITE_URL}",\n'
            '    "logo": {\n'
            '      "@type": "ImageObject",\n'
            f'      "url": "{_SITE_URL}/favicon.ico"\n'
            '    }\n'
            '  },\n'
            f'  "keywords": "{keywords}"\n'
            '}\n'
            '</script>'
        )

    def _build_breadcrumb_schema(self, blog: BlogPost, post_url: str = "") -> str:
        category = (blog.meta.tags[0] if blog.meta.tags else "Technology").strip()
        post_url_val = self._esc_json(post_url) if post_url else _SITE_URL
        return (
            '<script type="application/ld+json">\n'
            '{\n'
            '  "@context": "https://schema.org",\n'
            '  "@type": "BreadcrumbList",\n'
            '  "itemListElement": [\n'
            '    {\n'
            '      "@type": "ListItem",\n'
            '      "position": 1,\n'
            f'      "name": "{_SITE_NAME}",\n'
            f'      "item": "{_SITE_URL}"\n'
            '    },\n'
            '    {\n'
            '      "@type": "ListItem",\n'
            '      "position": 2,\n'
            f'      "name": "{self._esc_json(category)}",\n'
            f'      "item": "{_SITE_URL}/search/label/{self._esc_json(category.replace(" ", "%20"))}"\n'
            '    },\n'
            '    {\n'
            '      "@type": "ListItem",\n'
            '      "position": 3,\n'
            f'      "name": "{self._esc_json(blog.title)}",\n'
            f'      "item": "{post_url_val}"\n'
            '    }\n'
            '  ]\n'
            '}\n'
            '</script>'
        )

    def _build_faq_schema(self, body_html: str) -> str:
        """Extract FAQ Q&A pairs from post HTML and generate FAQPage schema."""
        faq_pattern = re.compile(
            r'<details class="ts-faq-item">\s*<summary>(.*?)</summary>\s*'
            r'<div class="ts-faq-answer">(.*?)</div>\s*</details>',
            re.DOTALL,
        )
        matches = faq_pattern.findall(body_html)
        if not matches:
            return ""

        items = []
        for question, answer in matches:
            q = self._esc_json(re.sub(r"<[^>]+>", "", question).strip())
            a = self._esc_json(re.sub(r"<[^>]+>", "", answer).strip())
            items.append(
                '    {\n'
                '      "@type": "Question",\n'
                f'      "name": "{q}",\n'
                '      "acceptedAnswer": {\n'
                '        "@type": "Answer",\n'
                f'        "text": "{a}"\n'
                '      }\n'
                '    }'
            )

        return (
            '<script type="application/ld+json">\n'
            '{\n'
            '  "@context": "https://schema.org",\n'
            '  "@type": "FAQPage",\n'
            '  "mainEntity": [\n'
            + ",\n".join(items) + "\n"
            '  ]\n'
            '}\n'
            '</script>'
        )

    def _build_og_meta(self, blog: BlogPost, post_url: str = "") -> str:
        """Open Graph + Twitter Card meta tags for social sharing previews."""
        title = self._esc(blog.title)
        desc = self._esc(blog.meta.meta_description or "")
        url_val = self._esc(post_url) if post_url else _SITE_URL
        image_url = self._esc(blog.featured_image_url or f"{_SITE_URL}/og-default.jpg")
        site_name = _SITE_NAME

        return (
            # Open Graph
            f'<meta property="og:type" content="article"/>'
            f'<meta property="og:title" content="{title}"/>'
            f'<meta property="og:description" content="{desc}"/>'
            f'<meta property="og:url" content="{url_val}"/>'
            f'<meta property="og:image" content="{image_url}"/>'
            f'<meta property="og:image:width" content="1200"/>'
            f'<meta property="og:image:height" content="630"/>'
            f'<meta property="og:site_name" content="{site_name}"/>'
            f'<meta property="article:author" content="{site_name}"/>'
            # Twitter Card
            f'<meta name="twitter:card" content="summary_large_image"/>'
            f'<meta name="twitter:title" content="{title}"/>'
            f'<meta name="twitter:description" content="{desc}"/>'
            f'<meta name="twitter:image" content="{image_url}"/>'
            f'<meta name="twitter:site" content="@tinkerstack"/>'
        )

    # -------------------------------------------------------------------------
    # Helpers
    # -------------------------------------------------------------------------

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
