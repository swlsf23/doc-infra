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
