import json
import logging
import sys
import time
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv
load_dotenv()

Path("logs").mkdir(exist_ok=True)
Path("reports").mkdir(exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)-8s %(name)s - %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler(
            Path("logs") / f"{datetime.now().strftime('%Y-%m-%d')}.log",
            encoding="utf-8",
        ),
    ],
)
logger = logging.getLogger(__name__)

from trend_scanner.scanner import TrendScanner
from blog_generator.generator import BlogGenerator
from publisher.blogger import BloggerPublisher
from notifications.telegram import send_report

REPORTS_DIR = Path("reports")


def run_daily_pipeline(topic_count: int = 25) -> dict:
    report = {
        "date": datetime.now().isoformat(),
        "topics_found": [],
        "blogs_published": [],
        "errors": [],
    }

    try:
        scanner = TrendScanner()
        topics = scanner.get_top_topics(count=topic_count)
        report["topics_found"] = [t.title for t in topics]
        logger.info(f"Found {len(topics)} trending topics")
    except Exception as e:
        msg = f"Trend scanning failed: {e}"
        report["errors"].append(msg)
        logger.critical(msg)
        _save_report(report)
        send_report(report)
        return report

    generator = BlogGenerator()
    publisher = BloggerPublisher.from_config()

    for i, topic in enumerate(topics):
        if i > 0:
            time.sleep(3)  # avoid Groq rate limit (30 req/min)
        try:
            logger.info(f"Processing topic {i+1}/{len(topics)}: {topic.title}")
            blog = generator.generate(topic)

            result = publisher.publish(blog)
            report["blogs_published"].append({
                "title": blog.title,
                "url": result.get("link", ""),
                "quality_score": blog.meta.quality_score,
                "seo_score": blog.meta.seo_score,
                "needs_review": blog.needs_review,
                "slug": blog.meta.slug,
            })
            logger.info(f"Published: {blog.title}")

        except Exception as e:
            msg = f"{topic.title}: {e}"
            report["errors"].append(msg)
            logger.error(f"Failed for topic '{topic.title}': {e}", exc_info=True)

    _save_report(report)
    send_report(report)

    logger.info(
        f"Pipeline complete — "
        f"{len(report['blogs_published'])} published, "
        f"{len(report['errors'])} errors"
    )
    return report


def _save_report(report: dict) -> None:
    date_str = report["date"][:10]
    path = REPORTS_DIR / f"{date_str}.json"
    path.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
    logger.info(f"Report saved to {path}")


if __name__ == "__main__":
    run_daily_pipeline()
