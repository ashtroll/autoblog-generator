import logging
import re
from datetime import datetime
from typing import Optional

from .llm_client import LLMClient
from .models import BlogPost, QualityReport, Topic
from .prompts import quality_check, research, writing
from .image_fetcher import fetch_image
from publisher.markdown_to_html import to_html

logger = logging.getLogger(__name__)

_MAX_RETRIES = 2


class BlogGenerator:
    def __init__(self, api_key: Optional[str] = None):
        self._llm = LLMClient(api_key=api_key)

    def generate(self, topic: Topic) -> BlogPost:
        logger.info(f"Generating blog for: {topic.title}")
        today = datetime.utcnow().strftime("%B %d, %Y")

        # Stage 1 — Research expansion
        research_text = self._llm.complete(
            system=research.SYSTEM,
            user_message=research.build(topic.title, topic.description, topic.source_urls, today=today),
        )

        # Pick the first suggested title from the research output
        chosen_title = self._pick_title(research_text, fallback=topic.title)

        # Stage 2 — Blog writing
        blog_md = self._llm.complete(
            system=writing.SYSTEM,
            user_message=writing.build(chosen_title, research_text, today=today),
            max_tokens=6000,
        )

        # Stage 3 — Quality + retry loop
        best_post: Optional[BlogPost] = None

        for attempt in range(_MAX_RETRIES + 1):
            review_data = self._llm.complete_json(
                system=quality_check.SYSTEM,
                user_message=quality_check.build(blog_md),
            )

            try:
                report = QualityReport.model_validate(review_data)
            except Exception as e:
                logger.warning(f"QualityReport parse error (attempt {attempt}): {e}")
                break

            image_data = None
            if report.image_search_term:
                image_data = fetch_image(report.image_search_term)

            post = BlogPost(
                topic=topic,
                title=chosen_title,
                content_md=blog_md,
                content_html=to_html(blog_md, featured_image_url=image_data["url"] if image_data else None, featured_image_credit=image_data["photographer"] if image_data else None),
                meta=report,
                featured_image_url=image_data["url"] if image_data else None,
                featured_image_credit=image_data["photographer"] if image_data else None,
                needs_review=not report.pass_,
            )

            if best_post is None or report.quality_score > best_post.meta.quality_score:
                best_post = post

            if report.pass_ and report.quality_score >= 7:
                logger.info(
                    f"Blog passed quality check (score={report.quality_score}, "
                    f"seo={report.seo_score}) on attempt {attempt}"
                )
                return post

            if attempt < _MAX_RETRIES and report.rewrite_instructions:
                logger.info(
                    f"Rewriting (attempt {attempt + 1}) — score={report.quality_score}: "
                    f"{report.rewrite_instructions[:80]}"
                )
                rewrite_prompt = (
                    f"Rewrite the blog post addressing these issues:\n"
                    f"{report.rewrite_instructions}\n\n"
                    f"Original post:\n{blog_md}"
                )
                blog_md = self._llm.complete(
                    system=writing.SYSTEM,
                    user_message=rewrite_prompt,
                    max_tokens=6000,
                )

        if best_post is None:
            # Fallback: return last draft without a valid report
            image_data = fetch_image(chosen_title)  # Use title as fallback search term

            best_post = BlogPost(
                topic=topic,
                title=chosen_title,
                content_md=blog_md,
                content_html=to_html(blog_md, featured_image_url=image_data["url"] if image_data else None, featured_image_credit=image_data["photographer"] if image_data else None),
                meta=QualityReport.model_validate({
                    "quality_score": 5,
                    "seo_score": 5,
                    "pass": False,
                    "meta_description": topic.description[:155],
                    "tags": [],
                    "slug": re.sub(r"[^\w-]", "-", topic.title.lower())[:60],
                    "estimated_read_time": "5 min read",
                    "image_search_term": chosen_title,
                    "issues": ["Quality check failed — manual review required"],
                }),
                featured_image_url=image_data["url"] if image_data else None,
                featured_image_credit=image_data["photographer"] if image_data else None,
                needs_review=True,
            )

        logger.warning(
            f"Blog for '{topic.title}' did not pass quality threshold — flagged for review"
        )
        return best_post

    @staticmethod
    def _pick_title(research_text: str, fallback: str) -> str:
        lines = research_text.splitlines()
        in_titles = False
        for line in lines:
            stripped = line.strip()
            # Detect the titles section header
            if re.search(r"(potential|blog post|seo).*(title|headline)", stripped, re.I):
                in_titles = True
                continue
            if in_titles:
                # Skip blank lines and section headers (lines ending with ":")
                if not stripped or stripped.endswith(":"):
                    continue
                # Strip leading numbering/bullets/bold markers
                candidate = re.sub(r"^[\d\.\-\*\#]+\s*|\*{1,2}", "", stripped).strip()
                # A real title: 15+ chars, not a meta-instruction sentence
                if len(candidate) >= 15 and not candidate.lower().startswith("here are"):
                    return candidate
        return fallback
