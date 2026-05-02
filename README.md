# TinkerStack — Automated Blog Generator

A fully automated pipeline that runs daily on GitHub Actions: scans for the top 25 trending topics, generates SEO-optimized blog posts using AI, and publishes them directly to Blogger — with zero manual work.

## How It Works

Every day at **6:00 AM IST**, the pipeline:

1. **Scans 300+ trending stories** from 5 sources (NewsAPI, Reddit, Google News RSS, HackerNews, Google Trends)
2. **Deduplicates and ranks** topics by recency + engagement score
3. **Picks the top 25** hottest topics of the day
4. **Generates a full blog post** for each topic using a 3-stage AI pipeline
5. **Publishes all 25 articles** live to Blogger via the Blogger API

---

## Project Structure

```
autoblog-generator/
├── main.py                          # Orchestrator: scan → generate → publish → report
├── config.py                        # Environment variable loading
├── requirements.txt
│
├── trend_scanner/
│   ├── scanner.py                   # Aggregates all sources → dedup → rank → top 25
│   ├── deduplicator.py              # rapidfuzz fuzzy matching (threshold 70%)
│   ├── ranker.py                    # Score = source_count × recency × engagement
│   └── sources/
│       ├── google_trends.py         # pytrends
│       ├── newsapi_source.py        # NewsAPI (6 categories)
│       ├── hackernews.py            # HackerNews top stories
│       ├── googlenews.py            # Google News RSS (6 feeds)
│       └── reddit.py               # Reddit hot posts (10 subreddits)
│
├── blog_generator/
│   ├── generator.py                 # 3-stage pipeline with retry loop
│   ├── llm_client.py                # Groq SDK wrapper (LLaMA 3.3 70B)
│   ├── models.py                    # Pydantic models: Topic, BlogPost, QualityReport
│   └── prompts/
│       ├── research.py              # Stage 1: research expansion
│       ├── writing.py               # Stage 2: blog writing
│       └── quality_check.py        # Stage 3: SEO + quality review with retry
│
├── publisher/
│   ├── blogger.py                   # Blogger API v3 with Google OAuth2
│   └── markdown_to_html.py         # mistune markdown → HTML converter
│
├── notifications/
│   └── telegram.py                  # Daily summary via Telegram Bot
│
├── dashboard/
│   └── app.py                       # Streamlit monitoring dashboard
│
├── setup/
│   ├── blogger_template.xml         # Custom Blogger XML theme (SEO-optimized)
│   └── seo_updater.py              # One-time script to add JSON-LD to existing posts
│
├── reports/                         # JSON report per run (gitignored)
├── logs/                            # Log files (gitignored)
└── .github/
    └── workflows/
        └── daily-blog.yml           # GitHub Actions cron job
```

---

## Blog Generation Pipeline

Each topic goes through a **3-stage AI pipeline** using Groq's LLaMA 3.3 70B:

```
Topic → [Stage 1: Research] → [Stage 2: Write] → [Stage 3: Quality Check]
                                                         ↓ score < 7?
                                                    [Rewrite] → max 2 retries
```

- **Stage 1 — Research:** Expands the topic into facts, angles, and 5 candidate titles
- **Stage 2 — Writing:** Produces a 900–1500 word blog post with today's date context
- **Stage 3 — Quality Check:** Returns JSON with quality score (0–10), SEO score, meta description, tags, slug, read time. If score < 7, rewrites with specific instructions (max 2 retries)

Each published post includes:
- JSON-LD structured data (schema.org BlogPosting) for SEO
- Reading time estimate
- Tag pills with label links
- Twitter / Facebook / WhatsApp share buttons
- CTA box

---

## Tech Stack

| Layer | Technology |
|---|---|
| AI / LLM | Groq API — LLaMA 3.3 70B Versatile (free tier) |
| Scheduler | GitHub Actions (cron, runs on GitHub's servers) |
| Publishing | Blogger API v3 + Google OAuth2 refresh token |
| Trend Sources | NewsAPI, Reddit JSON API, Google News RSS, HackerNews, pytrends |
| Deduplication | rapidfuzz fuzzy matching |
| Markdown → HTML | mistune |
| Dashboard | Streamlit |
| Notifications | Telegram Bot API |

---

## Setup

### 1. Clone the repo

```bash
git clone https://github.com/ashtroll/autoblog-generator.git
cd autoblog-generator
pip install -r requirements.txt
```

### 2. Configure environment variables

Copy `.env.example` to `.env` and fill in your keys:

```env
GROQ_API_KEY=your_groq_api_key
NEWSAPI_KEY=your_newsapi_key
GOOGLE_CLIENT_ID=your_google_client_id
GOOGLE_CLIENT_SECRET=your_google_client_secret
GOOGLE_REFRESH_TOKEN=your_google_refresh_token
BLOGGER_BLOG_ID=your_blogger_blog_id
BLOGGER_PUBLISHED=true
TELEGRAM_BOT_TOKEN=optional
TELEGRAM_CHAT_ID=optional
```

### 3. Get a Google Refresh Token

```bash
python get_refresh_token.py
```

Follow the OAuth2 flow in your browser. The refresh token is printed to the terminal.

### 4. Set GitHub Secrets

In your GitHub repo → Settings → Secrets → Actions, add each key from your `.env`.

### 5. Apply the Blogger template

In Blogger → Theme → ▼ → **Edit HTML**, paste the contents of `setup/blogger_template.xml`.

### 6. Run locally

```bash
python main.py
```

Or trigger manually via GitHub Actions → Daily Blog Generator → **Run workflow**.

---

## GitHub Actions Schedule

The workflow runs automatically every day:

```yaml
on:
  schedule:
    - cron: '30 0 * * *'   # 6:00 AM IST = 00:30 UTC
  workflow_dispatch:         # also triggerable manually
```

No server required. Runs entirely on GitHub's free infrastructure.

---

## Dashboard

```bash
streamlit run dashboard/app.py
```

Shows today's published articles, quality scores, topics found, and any errors — loaded from the `reports/` JSON files.

---

## License

MIT
