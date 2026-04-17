"""Markdown to HTML using Mistune (pure Python, BSD).

Relative ``*.md`` link/image targets are emitted as ``*.html`` so output matches
static files on disk. External URLs and non-``.md`` paths are unchanged.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Optional

import mistune
from mistune.renderers.html import HTMLRenderer

from pipeline.converters.base import DocumentConverter
from pipeline.converters.markdown.mistune.directives import directives


def _emit_static_href(url: str) -> str:
    """Map a relative ``page.md`` (or ``page.md#id``) to the built HTML path."""
    if not url or url.startswith(("#", "http://", "https://", "mailto:", "//")):
        return url
    if "#" in url:
        path, _, frag = url.partition("#")
        if not path.endswith(".md"):
            return url
        return f"{path[:-3]}.html#{frag}"
    if not url.endswith(".md"):
        return url
    return f"{url[:-3]}.html"


class DocInfraHTMLRenderer(HTMLRenderer):
    """Emits ``href``/``src`` for static HTML output from Markdown page links."""

    def link(self, text: str, url: str, title: Optional[str] = None) -> str:
        url = _emit_static_href(url)
        return super().link(text, url, title)

    def image(self, text: str, url: str, title: Optional[str] = None) -> str:
        url = _emit_static_href(url)
        return super().image(text, url, title)


class MistuneMarkdownConverter(DocumentConverter):
    """Markdown → HTML via Mistune; plugins + renderer above for correct page links."""

    def __init__(self, *, directives_enabled: bool = True) -> None:
        plugins: list[Any] = [
            "strikethrough",
            "footnotes",
            "table",
            "url",
            "task_lists",
        ]
        if directives_enabled:
            plugins.append(directives)
        self._md = mistune.create_markdown(
            renderer=DocInfraHTMLRenderer(),
            plugins=plugins,
        )

    @property
    def id(self) -> str:
        return "markdown"

    def convert(self, text: str, *, source_path: Path | None = None) -> str:
        return str(self._md(text))
