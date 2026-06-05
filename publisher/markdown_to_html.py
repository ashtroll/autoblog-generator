import re
import mistune
from typing import Optional


_md = mistune.create_markdown(
    plugins=["strikethrough", "table"],
)

_PULL_QUOTE_EMOJI = "💡📊📈⚡🔥💥🎯🚨📉⭐"


def _slugify(text: str) -> str:
    text = re.sub(r"<[^>]+>", "", text)
    text = text.lower().strip()
    text = re.sub(r"[^\w\s-]", "", text)
    text = re.sub(r"[\s_]+", "-", text)
    return text.strip("-")


def _add_heading_anchors(html: str) -> str:
    def repl(match):
        tag = match.group(1)
        inner = match.group(2)
        slug = _slugify(inner)
        return f'<{tag} id="{slug}">{inner}</{tag}>'
    return re.sub(r"<(h[2-3])>(.*?)</\1>", repl, html, flags=re.DOTALL)


def _style_tldr_box(html: str) -> str:
    pattern = re.compile(
        r'<blockquote>\s*<p>\s*<strong>TL;?DR</strong>\s*</p>\s*(.*?)</blockquote>',
        re.DOTALL | re.IGNORECASE,
    )

    def repl(match):
        inner = match.group(1)
        items = re.findall(r"<li>(.*?)</li>", inner, re.DOTALL)
        if not items:
            paragraphs = re.findall(r"<p>(.*?)</p>", inner, re.DOTALL)
            items = [p.strip() for p in paragraphs if p.strip()]
        if not items:
            return match.group(0)
        lis = "".join(f'<li>{item.strip()}</li>' for item in items)
        return (
            '<div class="ts-tldr">'
            '<div class="ts-tldr-label">Key Takeaways</div>'
            f'<ul>{lis}</ul>'
            '</div>'
        )

    return pattern.sub(repl, html)


def _style_toc(html: str) -> str:
    pattern = re.compile(
        r'(?:<p>)?\s*(?:<!--|&lt;!--)\s*TOC\s*(?:-->|--&gt;)\s*(?:</p>)?'
        r'(.*?)'
        r'(?:<p>)?\s*(?:<!--|&lt;!--)\s*/TOC\s*(?:-->|--&gt;)\s*(?:</p>)?',
        re.DOTALL | re.IGNORECASE,
    )

    def repl(match):
        inner = match.group(1).strip()
        ul_match = re.search(r'<ul>.*?</ul>', inner, re.DOTALL)
        list_html = ul_match.group(0) if ul_match else inner
        return (
            '<nav class="ts-toc" aria-label="Table of Contents">'
            '<div class="ts-toc-title">In this article</div>'
            f'{list_html}'
            '</nav>'
        )

    return pattern.sub(repl, html)


def _style_pull_quotes(html: str) -> str:
    emoji_class = re.escape(_PULL_QUOTE_EMOJI)
    pattern = re.compile(
        rf'<blockquote>\s*<p>\s*([{emoji_class}])\s*(.*?)</p>\s*</blockquote>',
        re.DOTALL,
    )

    def repl(match):
        emoji = match.group(1)
        body = match.group(2).strip()
        return (
            '<aside class="ts-pullquote">'
            f'<span class="ts-pullquote-icon" aria-hidden="true">{emoji}</span>'
            f'<span class="ts-pullquote-text">{body}</span>'
            '</aside>'
        )

    return pattern.sub(repl, html)


def _style_faq(html: str) -> str:
    faq_pattern = re.compile(
        r'(<h2[^>]*>(?:FAQ|Frequently Asked Questions)</h2>)(.*?)(?=<h2|$)',
        re.DOTALL | re.IGNORECASE,
    )

    def faq_repl(match):
        heading = match.group(1)
        body = match.group(2)

        item_pattern = re.compile(
            r'<h3[^>]*>(.*?)</h3>(.*?)(?=<h3|$)',
            re.DOTALL,
        )

        items_html = []
        for q_match in item_pattern.finditer(body):
            question = q_match.group(1).strip()
            answer = q_match.group(2).strip()
            items_html.append(
                '<details class="ts-faq-item">'
                f'<summary>{question}</summary>'
                f'<div class="ts-faq-answer">{answer}</div>'
                '</details>'
            )

        if not items_html:
            return match.group(0)

        return (
            f'{heading}'
            '<section class="ts-faq">'
            + "".join(items_html) +
            '</section>'
        )

    return faq_pattern.sub(faq_repl, html)


def _style_bottom_line(html: str) -> str:
    pattern = re.compile(
        r'(<h2[^>]*>The Bottom Line</h2>)(.*?)(?=<h2|$)',
        re.DOTALL | re.IGNORECASE,
    )

    def repl(match):
        heading = match.group(1)
        body = match.group(2).strip()
        return (
            '<section class="ts-bottom-line">'
            f'{heading}'
            f'{body}'
            '</section>'
        )

    return pattern.sub(repl, html)


def _add_lazy_loading(html: str) -> str:
    """Add loading=lazy + decoding=async to every <img> that doesn't already have them."""
    def repl(match):
        tag = match.group(0)
        if 'loading=' not in tag:
            tag = tag.replace('<img ', '<img loading="lazy" decoding="async" ', 1)
        return tag
    return re.sub(r'<img\b[^>]*>', repl, html)


def _add_external_link_attrs(html: str) -> str:
    """Add rel=noopener noreferrer + target=_blank to external links."""
    def repl(match):
        tag = match.group(0)
        href_match = re.search(r'href=["\']([^"\']*)["\']', tag)
        if not href_match:
            return tag
        href = href_match.group(1)
        # Only touch absolute URLs pointing away from the site
        if href.startswith("http") and "tinkerstackk.blogspot.com" not in href:
            if 'target=' not in tag:
                tag = tag.replace('<a ', '<a target="_blank" ', 1)
            if 'rel=' not in tag:
                tag = tag.replace('<a ', '<a rel="noopener noreferrer" ', 1)
            else:
                # Append to existing rel value
                tag = re.sub(r'rel="([^"]*)"', lambda m: f'rel="{m.group(1)} noopener noreferrer"', tag)
        return tag
    return re.sub(r'<a\b[^>]*>', repl, html)


def to_html(
    markdown_text: str,
    featured_image_url: Optional[str] = None,
    featured_image_credit: Optional[str] = None,
    title: Optional[str] = None,
) -> str:
    html = _md(markdown_text)
    html = _add_heading_anchors(html)
    html = _style_tldr_box(html)
    html = _style_toc(html)
    html = _style_pull_quotes(html)
    html = _style_faq(html)
    html = _style_bottom_line(html)
    html = _add_lazy_loading(html)
    html = _add_external_link_attrs(html)

    if featured_image_url:
        credit_html = ""
        if featured_image_credit:
            credit_html = (
                f'<figcaption class="ts-hero-credit">'
                f'Photo by {featured_image_credit} / Unsplash'
                f'</figcaption>'
            )
        alt_text = _escape_attr(title) if title else "Featured article image"
        # Derive a smaller mobile variant (400px wide) from the same base URL
        mobile_url = _resize_unsplash(featured_image_url, width=400, height=210)
        img_html = (
            '<figure class="ts-hero-figure">'
            f'<img src="{featured_image_url}" '
            f'srcset="{mobile_url} 400w, {featured_image_url} 800w" '
            f'sizes="(max-width:600px) 400px, 800px" '
            f'alt="{alt_text}" '
            f'loading="eager" decoding="async" width="800" height="420" '
            f'fetchpriority="high"/>'
            f'{credit_html}'
            '</figure>'
        )
        html = img_html + html

    return html


def _escape_attr(text: str) -> str:
    """Escape text for use in HTML attributes."""
    return (text or "").replace("&", "&amp;").replace('"', "&quot;").replace("<", "&lt;").replace(">", "&gt;")


def _resize_unsplash(url: str, width: int, height: int) -> str:
    """Return a resized variant of an Unsplash URL by replacing w/h params."""
    base = url.split("?")[0]
    return f"{base}?w={width}&h={height}&fit=crop&q=72&auto=format&fm=webp"
