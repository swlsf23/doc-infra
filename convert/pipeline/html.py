"""Turn converted body markup into a full HTML5 page.

The Markdown converter (Mistune today) returns an HTML **fragment**: the
inner elements only, with no ``<html>`` or ``<head>``. This module is where the
build pipeline completes the job for each output file. It supplies a small
fixed document shell so every generated page is valid standalone HTML you can
open in a browser or host as a static file.

The shell is intentionally thin: charset, viewport, and ``<title>`` only.
Site-wide layout, stylesheets, navigation, and extra metadata tags are out of
scope here for now. Those can be added later (for example more ``<meta>`` tags
or a shared template) without changing how converters work.

Security note: ``<title>`` text is escaped because it comes from document titles
or file names. The ``body_html`` argument is inserted verbatim. It is produced
by our converter pipeline, not raw author HTML, so we treat it as trusted
markup. If that assumption ever changes, body escaping or sanitization would
need to happen here or in the converter.
"""

from __future__ import annotations

import html
import re
from pathlib import Path

from bs4 import BeautifulSoup

_TITLE_RE = re.compile(r"<title[^>]*>(.*?)</title>", re.IGNORECASE | re.DOTALL)
_BODY_RE = re.compile(r"<body[^>]*>(.*?)</body>", re.IGNORECASE | re.DOTALL)
_H1_RE = re.compile(r"<h1[^>]*>(.*?)</h1>", re.IGNORECASE | re.DOTALL)
_HEADING_RE = re.compile(r"^h[1-6]$", re.IGNORECASE)
_BLOCK_TAGS = {
    "aside",
    "article",
    "blockquote",
    "div",
    "dl",
    "ol",
    "p",
    "pre",
    "section",
    "table",
    "ul",
}
_ADMONITION_TITLE_LINE_RE = re.compile(
    r"^\s*<(?:p|h[1-6]|strong)\b[^>]*>(.*?)</(?:p|h[1-6]|strong)>\s*",
    re.IGNORECASE | re.DOTALL,
)


def _render_canonical_admonition(kind: str, title: str, body_html: str) -> str:
    return (
        f'<aside class="admonition admonition-{kind}" role="note">\n'
        f'<p class="admonition-title">{html.escape(title, quote=False)}</p>\n'
        f'<div class="admonition-body">\n{body_html.strip()}\n</div>\n'
        f"</aside>"
    )


def _normalize_admonition_block(inner_html: str, default_title: str, kind: str) -> str:
    inner = inner_html.strip()
    title = default_title

    m_callout = re.match(
        r'\s*<p\b[^>]*class="[^"]*\bcallout-title\b[^"]*"[^>]*>(.*?)</p>\s*',
        inner,
        flags=re.IGNORECASE | re.DOTALL,
    )
    if m_callout:
        title_text = _collapse_text(m_callout.group(1)).rstrip(":")
        if title_text:
            title = title_text
        inner = inner[m_callout.end() :].lstrip()
    else:
        m_title = _ADMONITION_TITLE_LINE_RE.match(inner)
        if m_title:
            title_text = _collapse_text(m_title.group(1)).rstrip(":")
            if title_text:
                title = title_text
            inner = inner[m_title.end() :].lstrip()

    return _render_canonical_admonition(kind=kind, title=title, body_html=inner)


def normalize_html_admonitions(fragment_html: str) -> str:
    """Normalize common raw HTML callout/admonition variants to canonical markup."""
    out = fragment_html

    out = re.sub(
        r'<aside\b[^>]*class="[^"]*\bnote\b[^"]*"[^>]*>(.*?)</aside>',
        lambda m: _normalize_admonition_block(m.group(1), default_title="Note", kind="note"),
        out,
        flags=re.IGNORECASE | re.DOTALL,
    )
    out = re.sub(
        r'<div\b[^>]*class="[^"]*\balert-warning\b[^"]*"[^>]*>(.*?)</div>',
        lambda m: _normalize_admonition_block(m.group(1), default_title="Warning", kind="warning"),
        out,
        flags=re.IGNORECASE | re.DOTALL,
    )
    out = re.sub(
        r'<section\b[^>]*class="[^"]*\bcallout\b[^"]*\bcaution\b[^"]*"[^>]*>(.*?)</section>',
        lambda m: _normalize_admonition_block(m.group(1), default_title="Caution", kind="caution"),
        out,
        flags=re.IGNORECASE | re.DOTALL,
    )

    return out


def _repair_heading_block_nesting(soup: BeautifulSoup) -> None:
    """Move block-level children out of headings if malformed input nests them."""
    if soup.body is None:
        return
    for heading in soup.body.find_all(_HEADING_RE):
        extracted_blocks = []
        for child in list(heading.contents):
            child_name = getattr(child, "name", None)
            if child_name and child_name.lower() in _BLOCK_TAGS:
                extracted_blocks.append(child.extract())
        if not extracted_blocks:
            continue
        anchor = heading
        for node in extracted_blocks:
            anchor.insert_after(node)
            anchor = node


def _collapse_text(value: str) -> str:
    text = re.sub(r"<[^>]+>", " ", value)
    text = html.unescape(text)
    return re.sub(r"\s+", " ", text).strip()


def title_from_markdown_or_path(markdown: str, source_path: Path) -> str:
    """Pick a human-readable page title for ``<title>`` and related uses.

    Order of preference:

    1. The text of the first Markdown ATX heading (a line that looks like
       ``# Some title``). That matches how authors usually name a page.
    2. If there is no such heading, derive a title from the source file name:
       use the stem (no extension), turn hyphens and underscores into spaces,
       and title-case the result so ``getting-started`` becomes
       ``Getting Started``.
    3. If the stem is empty, fall back to the full file name.

    The returned string is plain text. Callers pass it to
    :func:`wrap_fragment_html`, which escapes it for safe use inside HTML.
    """
    m = re.search(r"^\s*#\s+(.+)$", markdown, re.MULTILINE)
    if m:
        return m.group(1).strip()
    stem = source_path.stem.replace("-", " ").replace("_", " ")
    return stem.title() if stem else source_path.name


def title_from_html_or_path(raw_html: str, source_path: Path) -> str:
    """Pick a title from HTML (<title>, then first <h1>, then file name)."""
    tm = _TITLE_RE.search(raw_html)
    if tm:
        title_text = _collapse_text(tm.group(1))
        if title_text:
            return title_text
    hm = _H1_RE.search(raw_html)
    if hm:
        heading_text = _collapse_text(hm.group(1))
        if heading_text:
            return heading_text
    stem = source_path.stem.replace("-", " ").replace("_", " ")
    return stem.title() if stem else source_path.name


def body_fragment_from_html_source(raw_html: str) -> str:
    """Parse with a tolerant HTML5 parser and return normalized body fragment."""
    soup = BeautifulSoup(raw_html, "html5lib")
    _repair_heading_block_nesting(soup)
    body = soup.body
    if body is None:
        fragment = raw_html.strip()
    else:
        fragment = "".join(str(child) for child in body.contents).strip()
    return normalize_html_admonitions(fragment)


def wrap_fragment_html(title: str, body_html: str) -> str:
    """Embed ``body_html`` in a minimal HTML5 document and return the full page.

    ``body_html`` should be the converter output for one page (paragraphs,
    lists, links, and so on). This function does not parse or validate it. It
    only wraps it in a document skeleton.

    The template includes:

    - ``<!DOCTYPE html>`` and ``lang="en"`` on the root element for a valid
      HTML5 document and a default language hint for assistive tech and search.
    - ``<meta charset="utf-8">`` so browsers interpret bytes as UTF-8.
    - A viewport meta tag so the page scales sensibly on phones when opened
      as a local file or on a simple static host.
    - ``<title>`` filled from the ``title`` argument after HTML escaping.

    Authors can extend this function later with more head content (Open Graph,
    ``<link rel="stylesheet">``, inline critical CSS, and so on) while keeping
    converters focused on body markup only.
    """
    safe_title = html.escape(title, quote=True)
    # body_html is trusted converter output (see module docstring).
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{safe_title}</title>
</head>
<body>
{body_html}
</body>
</html>
"""
