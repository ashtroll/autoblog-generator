SYSTEM = (
    "You are a senior research analyst. Your job is to expand a trending topic into "
    "rich context that a blog writer can use. Be specific, data-driven, and concise."
)

TEMPLATE = """\
Given this trending topic, provide a structured research brief:

1. Key facts and recent developments (last 48 hours if known)
2. Why this topic is trending right now
3. 3–4 unique angles a blog post could take (avoid generic takes)
4. Target audience segments who care about this
5. Five potential blog post titles — SEO-optimized, curiosity-driven, no clickbait

Topic: {title}
Context: {description}
Source URLs: {source_urls}

Respond in plain text with clear numbered sections.
"""


def build(title: str, description: str, source_urls: list[str]) -> str:
    urls = "\n".join(source_urls) if source_urls else "none"
    return TEMPLATE.format(title=title, description=description, source_urls=urls)
