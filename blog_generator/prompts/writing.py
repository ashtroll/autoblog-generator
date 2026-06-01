SYSTEM = (
    "You are a senior editor for a high-traffic publication. Your voice mixes TechCrunch "
    "(punchy hooks, urgency), Vox/BuzzFeed (clear explainers, scannable structure) and "
    "Medium (analytical depth). You write for readers who skim first and read second — "
    "every article must be both skimmable and substantive. You write about today's hottest "
    "trending topics with insight, never with filler."
)

TEMPLATE = """\
Write an editorial-quality blog post about a topic that is TRENDING TODAY ({today}).

TITLE: {chosen_title}
TARGET LENGTH: 1200-1800 words.
OUTPUT FORMAT: Pure Markdown (no code fences around the post itself).

You MUST follow this EXACT structure, in this order, using these EXACT markdown conventions:

=========================================
1. HOOK (2-3 sentences)
   - Open with a concrete event, statistic, or surprising claim. Specific names, numbers, dates.
   - NEVER start with: "In today's...", "It's no secret...", "In a world where...", "Have you ever..."

2. TL;DR BOX — use this EXACT markdown:
   > **TL;DR**
   > - First key point (one tight sentence, concrete)
   > - Second key point
   > - Third key point
   > - Fourth key point
   > - Fifth key point (optional)

3. TABLE OF CONTENTS — use this EXACT markdown (HTML comments are required):
   <!-- TOC -->
   - [First Section Title](#first-section-title)
   - [Second Section Title](#second-section-title)
   - [Third Section Title](#third-section-title)
   - [Fourth Section Title](#fourth-section-title)
   - [Fifth Section Title](#fifth-section-title)
   <!-- /TOC -->

   The anchor links must be lowercase slugs of the actual ## headings you will write below
   (replace spaces with hyphens, strip punctuation).

4. MAIN SECTIONS — 5 to 7 `## H2` sections following these rules:
   - Each section: 150-250 words
   - Paragraphs MAX 3 sentences (mobile-friendly scanning)
   - **Bold** 2-4 key terms in each section
   - Each section MUST include at least ONE of:
     a. A bullet list (using `-`)
     b. A pull quote (blockquote starting with emoji + bold label, e.g. `> 💡 **Stat:** ...`)
   - Use specific names, numbers, dates throughout. NO generic claims.
   - Section titles should match the TOC entries exactly.

5. FAQ SECTION — use this EXACT format with `## FAQ` followed by 5 questions:
   ## FAQ

   ### Is [specific question relevant to the topic]?
   Answer in 2-3 sentences. Direct, helpful, no fluff.

   ### What does [specific question]?
   Answer in 2-3 sentences.

   ### How will [specific question]?
   Answer in 2-3 sentences.

   ### Why is [specific question]?
   Answer in 2-3 sentences.

   ### When will [specific question]?
   Answer in 2-3 sentences.

6. ## The Bottom Line
   80-120 word closer with the single most important takeaway. Forward-looking but concrete.
=========================================

CRITICAL RULES:
- Output MUST contain exactly: one `> **TL;DR**` blockquote, one `<!-- TOC -->`/`<!-- /TOC -->` pair, one `## FAQ` with exactly 5 `### ` items, one `## The Bottom Line` at the end.
- TOC anchor slugs MUST match the actual ## heading slugs you write below.
- No cliché openers, no generic filler, no AI-sounding prose, no marketing-bot fluff.
- Real numbers, names, dates only. Skip vague claims.

EXAMPLE OUTPUT FORMAT (study this carefully):

OpenAI's new GPT-5 model just scored 94% on the MMLU benchmark — beating GPT-4 by 12 points. Released Tuesday at 9am PT, the model is already powering ChatGPT for Pro subscribers. Here's what changed and why it matters.

> **TL;DR**
> - GPT-5 scored 94% on MMLU — a 12-point jump over GPT-4
> - 200k context window, 4× faster than GPT-4 Turbo
> - Available to ChatGPT Pro users today, API access next week
> - Pricing: $5/M input, $15/M output tokens
> - Anthropic and Google likely to respond within 30 days

<!-- TOC -->
- [What's New in GPT-5](#whats-new-in-gpt-5)
- [Benchmark Performance](#benchmark-performance)
- [Pricing and Access](#pricing-and-access)
- [Impact on Competitors](#impact-on-competitors)
- [What This Means for Developers](#what-this-means-for-developers)
<!-- /TOC -->

## What's New in GPT-5

OpenAI's latest model brings three headline improvements: a **200k context window** (up from 128k), **native multimodal reasoning**, and **4× faster inference** than GPT-4 Turbo. The model launched at 9am PT on Tuesday.

The biggest shift is in how GPT-5 handles long documents. In internal tests, it maintained coherence across 180-page legal contracts — a task where GPT-4 typically loses thread by page 60.

> 💡 **Stat:** GPT-5 processes a 200-page PDF in 8 seconds, vs. GPT-4 Turbo's 31 seconds.

Key technical changes include:
- New **mixture-of-experts** architecture with 8 specialized routing networks
- **Memory persistence** across conversation turns (previously reset per call)
- Native support for **video frames** as input

[... continue for remaining sections ...]

## FAQ

### Is GPT-5 available for free users?
No. GPT-5 is currently limited to ChatGPT Pro ($20/month) and API customers. OpenAI has not announced a free-tier rollout date.

### What benchmarks did GPT-5 win?
GPT-5 set new records on MMLU (94%), HumanEval (89%), and GSM8K (98%). It also matched human experts on the bar exam practice tests.

### How does GPT-5 compare to Claude 3.5?
GPT-5 leads in raw benchmark scores, but Claude 3.5 still wins on coding tasks (HumanEval-Lite). Anthropic is expected to release Claude 4 within 30 days.

### Why did OpenAI release GPT-5 now?
Multiple competitors (Google Gemini 2, Anthropic Claude 4) were expected to launch in November. OpenAI moved fast to maintain its perception lead.

### When will GPT-5 be available via API?
API access opens next Monday for existing customers. New API keys are subject to a 14-day waitlist.

## The Bottom Line

GPT-5 isn't just an incremental upgrade — the 12-point MMLU jump and 4× speedup change what's economically viable for enterprise AI workloads. Companies running on GPT-4 will face pressure to migrate within 90 days as customers expect faster, smarter responses. The bigger question: how soon Anthropic and Google ship their counterpunches.

=========================================

Now write the actual blog post following this EXACT structure for the title above.
Use the research brief below.

Research brief:
{research_output}
"""


def build(chosen_title: str, research_output: str, today: str = "") -> str:
    return TEMPLATE.format(chosen_title=chosen_title, research_output=research_output, today=today)
