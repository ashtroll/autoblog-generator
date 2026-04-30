import logging
import os
import requests

logger = logging.getLogger(__name__)

_API = "https://api.telegram.org/bot{token}/sendMessage"


def send_report(report: dict) -> None:
    token = os.getenv("TELEGRAM_BOT_TOKEN", "")
    chat_id = os.getenv("TELEGRAM_CHAT_ID", "")

    if not token or not chat_id:
        logger.info("Telegram not configured — skipping notification")
        return

    date = report.get("date", "")[:10]
    published = report.get("blogs_published", [])
    errors = report.get("errors", [])

    lines = [
        f"*Auto Blog Report — {date}*",
        "",
        f"Topics scanned: {len(report.get('topics_found', []))}",
        f"Blogs published: {len(published)}",
        f"Errors: {len(errors)}",
        "",
    ]

    for blog in published:
        score = blog.get("quality_score", "?")
        url = blog.get("url", "")
        title = blog.get("title", "untitled")
        if url:
            lines.append(f"✅ [{title}]({url}) — Q:{score}")
        else:
            lines.append(f"✅ {title} — Q:{score}")

    if errors:
        lines.append("")
        for err in errors:
            lines.append(f"❌ {err}")

    message = "\n".join(lines)

    try:
        resp = requests.post(
            _API.format(token=token),
            json={"chat_id": chat_id, "text": message, "parse_mode": "Markdown"},
            timeout=10,
        )
        resp.raise_for_status()
        logger.info("Telegram report sent")
    except Exception as e:
        logger.warning(f"Telegram notification failed: {e}")
