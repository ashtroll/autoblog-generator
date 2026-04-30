SYSTEM = (
    "You are an expert blog writer known for conversational authority and zero fluff. "
    "Your posts feel written by a sharp, well-informed human, not a marketing bot. "
    "You write about today's hottest trending topics with urgency and insight."
)

TEMPLATE = """\
Write a comprehensive, engaging blog post about a topic that is TRENDING TODAY ({today}).

REQUIREMENTS:
- Title: {chosen_title}
- Length: 900–1500 words
- Tone: Conversational but authoritative. Feel urgent — this is happening NOW.
- Structure: Hook (why this matters TODAY, 2–3 sentences) → What's happening → Why it matters → Analysis → Key takeaways
- Include: Specific data points, real examples, why readers should care right now
- SEO: Naturally include the primary keyword 3–5 times
- Opening: Must reference that this is a current, breaking, or fast-moving story
- End with: A forward-looking question or clear insight about what happens next

DO NOT:
- Use cliché openers ("In today's fast-paced world", "It's no secret that")
- Write generic background filler — assume the reader knows basics
- Use more than one bullet list per post
- Sound like AI wrote it
- Write evergreen content — this post must feel timely

Output the post in Markdown format (use ## for section headings, **bold** for key terms).

Research brief:
{research_output}
"""


def build(chosen_title: str, research_output: str, today: str = "") -> str:
    return TEMPLATE.format(chosen_title=chosen_title, research_output=research_output, today=today)
