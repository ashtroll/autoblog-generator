SYSTEM = (
    "You are an expert editor and SEO specialist. Review blog posts critically against modern "
    "editorial standards and engagement best practices. Return only valid JSON — no markdown "
    "fences, no prose."
)

TEMPLATE = """\
Review the blog post below and return a JSON object with exactly these fields:

{{
  "quality_score": <integer 1-10, writing quality + accuracy + insight>,
  "seo_score": <integer 1-10, keyword usage + meta description + structure for search>,
  "engagement_score": <integer 1-10, scannability + retention features + reader hooks>,
  "pass": <true if ALL: quality_score >= 7 AND seo_score >= 6 AND engagement_score >= 6 AND all required structure_checks are present>,
  "meta_description": "<155 chars max, compelling summary>",
  "tags": ["Primary Keyword", "Secondary Keyword", "Topic Category", "Subtopic", "Related Term"],
  "slug": "url-friendly-slug-from-title",
  "estimated_read_time": "X min read",
  "image_search_term": "<one or two keywords to fetch a relevant image from Unsplash>",
  "structure_checks": {{
    "has_tldr": <true if post contains a `> **TL;DR**` blockquote near the top>,
    "has_toc": <true if post contains `<!-- TOC -->` and `<!-- /TOC -->` markers with a list of jump links>,
    "has_faq": <true if post contains a `## FAQ` section>,
    "faq_count": <integer count of `### ` questions inside the FAQ section>,
    "has_bottom_line": <true if post ends with `## The Bottom Line` section>,
    "avg_paragraph_sentences": <integer estimate of average sentences per paragraph>,
    "uses_bold_terms": <true if 2+ **bold** terms appear in body sections>,
    "has_pull_quotes": <true if at least one blockquote starts with an emoji + bold label, e.g. `> 💡 **Stat:**`>
  }},
  "issues": ["<specific issue if any>"],

NOTE on tags: provide exactly 5-8 tags in Title Case (e.g. "Artificial Intelligence", "Climate Change"). Always include at least one matching a main site category: Technology, AI, Business, Science, or World. Use natural readable phrases, NOT hyphenated-lowercase. No generic filler like "Article" or "Blog Post".
  "rewrite_instructions": "<only present if pass is false — specific, actionable fixes>"
}}

PASS CRITERIA (all must be true):
- quality_score >= 7 AND seo_score >= 6 AND engagement_score >= 6
- structure_checks.has_tldr == true
- structure_checks.has_toc == true
- structure_checks.has_faq == true
- structure_checks.faq_count >= 5
- structure_checks.has_bottom_line == true

If any pass criterion fails, set "pass": false and include specific "rewrite_instructions"
naming exactly which sections to add/fix (e.g., "Add a TL;DR blockquote after the hook with
3-5 bullet points; the current post is missing it.").

Blog post:
{blog_content}
"""


def build(blog_content: str) -> str:
    return TEMPLATE.format(blog_content=blog_content)
