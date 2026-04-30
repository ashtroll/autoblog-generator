import mistune


_md = mistune.create_markdown(
    plugins=["strikethrough", "table"],
)


def to_html(markdown_text: str) -> str:
    return _md(markdown_text)
