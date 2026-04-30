SYSTEM = (
    "You are an expert blog writer known for conversational authority and zero fluff. "
    "Your posts feel written by a knowledgeable human, not a marketing bot."
)

TEMPLATE = """\
Write a comprehensive, engaging blog post using the research brief below.

REQUIREMENTS:
- Title: {chosen_title}
- Length: 800–1500 words
- Tone: Conversational but authoritative. No fluff.
- Structure: Hook intro (2–3 sentences) → Context → Analysis → Implications → Takeaways
- Include: Specific data points, real examples, expert perspective where applicable
- SEO: Naturally include the primary keyword 3–5 times
- End with: A thought-provoking question or clear call-to-action

DO NOT:
- Use cliché openers ("In today's fast-paced world", "It's no secret that")
- Write generic filler paragraphs
- Use more than one bullet list per post
- Sound like AI wrote it

Output the post in Markdown format (use ## for section headings, **bold** for key terms).

Research brief:
{research_output}
"""


def build(chosen_title: str, research_output: str) -> str:
    return TEMPLATE.format(chosen_title=chosen_title, research_output=research_output)
