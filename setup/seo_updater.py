"""
One-time script: updates all existing Blogger posts to add
JSON-LD structured data and better SEO formatting.
"""
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from dotenv import load_dotenv
load_dotenv()

import requests
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request

BLOG_ID = os.environ["BLOGGER_BLOG_ID"]
API = "https://www.googleapis.com/blogger/v3"


def get_token():
    creds = Credentials(
        token=None,
        refresh_token=os.environ["GOOGLE_REFRESH_TOKEN"],
        token_uri="https://oauth2.googleapis.com/token",
        client_id=os.environ["GOOGLE_CLIENT_ID"],
        client_secret=os.environ["GOOGLE_CLIENT_SECRET"],
    )
    creds.refresh(Request())
    return creds.token


def add_structured_data(post: dict, token: str):
    title = post["title"]
    url = post.get("url", "")
    published = post.get("published", "")
    content = post.get("content", "")

    schema = f"""
<script type="application/ld+json">
{{
  "@context": "https://schema.org",
  "@type": "BlogPosting",
  "headline": "{title.replace('"', '&quot;')}",
  "url": "{url}",
  "datePublished": "{published}",
  "author": {{
    "@type": "Organization",
    "name": "TinkerStack"
  }},
  "publisher": {{
    "@type": "Organization",
    "name": "TinkerStack",
    "url": "https://tinkerstackk.blogspot.com"
  }}
}}
</script>
"""
    if "application/ld+json" in content:
        print(f"  Skipping (already has schema): {title[:60]}")
        return

    updated_content = schema + content

    resp = requests.put(
        f"{API}/blogs/{BLOG_ID}/posts/{post['id']}",
        json={"title": title, "content": updated_content},
        headers={"Authorization": f"Bearer {token}"},
        timeout=15,
    )
    if resp.ok:
        print(f"  Updated: {title[:60]}")
    else:
        print(f"  Failed ({resp.status_code}): {title[:60]}")


def run():
    token = get_token()
    resp = requests.get(
        f"{API}/blogs/{BLOG_ID}/posts",
        params={"maxResults": 50},
        headers={"Authorization": f"Bearer {token}"},
        timeout=10,
    )
    posts = resp.json().get("items", [])
    print(f"Found {len(posts)} posts. Adding structured data...")
    for post in posts:
        add_structured_data(post, token)
    print("Done.")


if __name__ == "__main__":
    run()
