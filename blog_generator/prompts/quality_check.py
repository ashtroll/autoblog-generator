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
  "pass": <true if ALL pass criteria below are met>,
  "meta_description": "<150-160 chars, ideally starts with the primary keyword, compelling CTA>",
  "tags": ["Primary Keyword", "Secondary Keyword", "Topic Category", "Subtopic", "Related Term"],
  "slug": "primary-keyword-rich-url-slug",
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
    "has_pull_quotes": <true if at least one blockquote starts with an emoji + bold label, e.g. `> 💡 **Stat:**`>,
    "keyword_in_first_100_words": <true if the primary keyword (first tag) appears within the first 100 words of the post body>,
    "keyword_in_h1": <true if the primary keyword appears in the post title/H1>,
    "keyword_in_min_2_h2s": <true if the primary keyword or a close variant appears in at least 2 ## H2 section headings>,
    "meta_description_has_keyword": <true if the meta_description field starts with or contains the primary keyword>,
    "has_internal_link_opportunity": <true if the post mentions a topic that could naturally link to another article on the same tech blog>
  }},
  "issues": ["<specific issue — be concrete, e.g. 'primary keyword missing from first paragraph'>"],

NOTE on tags: provide exactly 5-8 tags in Title Case (e.g. "Artificial Intelligence", "Climate Change"). Always include at least one matching a main site category: Technology, AI, Business, Science, or World. Use natural readable phrases, NOT hyphenated-lowercase. No generic filler like "Article" or "Blog Post".

NOTE on slug: must be keyword-rich, 3-6 words, lowercase hyphenated. Strip stop words. Example: "gpt-5-benchmark-results" not "openai-releases-new-gpt-5-model-that-beats-all-competitors".

  "rewrite_instructions": "<only present if pass is false — list every failing criterion with a specific, actionable fix>"
}}

PASS CRITERIA (ALL must be true — no exceptions):
- quality_score >= 7
- seo_score >= 7
- engagement_score >= 6
- structure_checks.has_tldr == true
- structure_checks.has_toc == true
- structure_checks.has_faq == true
- structure_checks.faq_count >= 5
- structure_checks.has_bottom_line == true
- structure_checks.keyword_in_first_100_words == true
- structure_checks.keyword_in_h1 == true
- structure_checks.keyword_in_min_2_h2s == true

If any pass criterion fails, set "pass": false and include specific "rewrite_instructions"
naming exactly which criteria failed and what to fix. Example:
  "Primary keyword 'AI agents' is missing from the first paragraph — weave it naturally
   into the opening hook. Also add keyword to at least 2 H2 headings (currently 0)."

Blog post:
{blog_content}
"""


def build(blog_content: str) -> str:
    return TEMPLATE.format(blog_content=blog_content)
