SYSTEM = (
    "You are an expert editor and SEO specialist. Review blog posts critically and "
    "return only valid JSON — no markdown fences, no prose."
)

TEMPLATE = """\
Review the blog post below and return a JSON object with exactly these fields:

{{
  "quality_score": <integer 1–10>,
  "seo_score": <integer 1–10>,
  "pass": <true if quality_score >= 7 and seo_score >= 6, else false>,
  "meta_description": "<155 chars max, compelling summary>",
  "tags": ["tag1", "tag2", "tag3"],
  "slug": "url-friendly-slug-from-title",
  "estimated_read_time": "X min read",
  "image_search_term": "<one or two keywords to fetch a relevant image from Unsplash>",
  "issues": ["<specific issue if any>"],
  "rewrite_instructions": "<only present if pass is false — specific fixes>"
}}

Blog post:
{blog_content}
"""


def build(blog_content: str) -> str:
    return TEMPLATE.format(blog_content=blog_content)
