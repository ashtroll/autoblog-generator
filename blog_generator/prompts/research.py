SYSTEM = (
    "You are a senior research analyst. Your job is to expand a trending topic into "
    "rich context that a blog writer can use. Be specific, data-driven, and concise. "
    "Focus on what is happening RIGHT NOW — today's developments, not background history."
)

TEMPLATE = """\
Today's date: {today}

This is one of today's TOP TRENDING topics. Provide a research brief a blog writer can use to publish within the next hour:

1. Key facts and breaking developments (focus on the last 24-48 hours)
2. WHY this is trending RIGHT NOW — what triggered it today
3. 3–4 unique angles (avoid generic takes, pick angles that feel urgent or surprising)
4. Who is most affected / most interested in this right now
5. Five blog post titles — SEO-optimized, curiosity-driven, feels urgent and timely

Topic: {title}
Context: {description}
Source URLs: {source_urls}

Respond in plain text with clear numbered sections.
"""


def build(title: str, description: str, source_urls: list[str], today: str = "") -> str:
    urls = "\n".join(source_urls) if source_urls else "none"
    return TEMPLATE.format(title=title, description=description, source_urls=urls, today=today)
