import mistune
from typing import Optional


_md = mistune.create_markdown(
    plugins=["strikethrough", "table"],
)


def to_html(markdown_text: str, featured_image_url: Optional[str] = None, featured_image_credit: Optional[str] = None) -> str:
    html = _md(markdown_text)

    if featured_image_url:
        img_html = f'<figure style="margin: 20px 0; text-align: center;"><img src="{featured_image_url}" alt="Featured image" style="max-width: 100%; height: auto; border-radius: 8px;"/>'
        if featured_image_credit:
            img_html += f'<figcaption style="font-size: 0.9em; color: #666; margin-top: 8px;">Photo by {featured_image_credit}</figcaption>'
        img_html += '</figure>'
        html = img_html + html

    return html
