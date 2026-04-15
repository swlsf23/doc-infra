"""Mistune block directives plugin (`::: kind` … `:::`).

Syntax::

    ::: caution
    Body text runs **inline** markdown here.
    :::

Optional title on the opening line::

    ::: caution Watch out
    …
    :::
"""

from __future__ import annotations

import re
from typing import TYPE_CHECKING, Any, Dict, Optional

from mistune.util import escape

if TYPE_CHECKING:
    from mistune.block_parser import BlockParser
    from mistune.core import BlockState
    from mistune.markdown import Markdown

__all__ = ["directives", "admonition"]

# Opening line only — use [ \t] before $ so \s cannot span across newlines.
_ADMONITION_OPEN = (
    r"^ {0,3}:::\s+"
    r"(?P<adh_kind>[a-zA-Z][a-zA-Z0-9_-]*)"
    r"(?:[ \t]+(?P<adh_title>[^\n]+?))?"
    r"[ \t]*$"
)

_CLOSING_LINE = re.compile(r"^ {0,3}:::\s*$", re.M)

_ADMONITION_TITLES: Dict[str, str] = {
    "caution": "Caution",
    "warning": "Warning",
    "note": "Note",
}


def _safe_kind(kind: str) -> str:
    k = re.sub(r"[^a-z0-9_-]+", "", kind.lower())
    return k or "note"


def parse_admonition(block: "BlockParser", m: re.Match[str], state: "BlockState") -> Optional[int]:
    del block
    start = m.end()
    mc = _CLOSING_LINE.search(state.src, start)
    if not mc:
        return None

    kind_raw = m.group("adh_kind").lower()
    if kind_raw not in _ADMONITION_TITLES:
        return None
    title_raw = m.group("adh_title")
    title = title_raw.strip() if title_raw else None

    body = state.src[start : mc.start()].strip("\n")
    token: Dict[str, Any] = {
        "type": "admonition",
        "attrs": {"kind": kind_raw, "title": title},
        "text": body,
    }
    state.append_token(token)
    return mc.end()


def render_admonition(_renderer: Any, text: str, kind: str, title: Optional[str] = None) -> str:
    safe = _safe_kind(kind)
    if not title:
        title = _ADMONITION_TITLES.get(kind.lower(), "Note")
    title_html = '<p class="admonition-title">' + escape(title) + "</p>\n"
    return (
        f'<aside class="admonition admonition-{safe}" role="note">\n'
        f"{title_html}"
        f'<div class="admonition-body">\n{text}</div>\n'
        f"</aside>\n"
    )


def directives(md: "Markdown") -> None:
    md.block.register(
        "admonition",
        _ADMONITION_OPEN,
        parse_admonition,
        before="fenced_code",
    )
    if md.renderer and md.renderer.NAME == "html":
        md.renderer.register("admonition", render_admonition)


# Backward-compatible alias for older imports.
admonition = directives
