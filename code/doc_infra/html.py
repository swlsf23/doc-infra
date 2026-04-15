"""Minimal HTML page wrapper for standalone preview."""

from __future__ import annotations

import html
import re
from pathlib import Path


def title_from_markdown_or_path(markdown: str, source_path: Path) -> str:
    """First line ``# heading`` if present, else title-cased stem."""
    m = re.search(r"^\s*#\s+(.+)$", markdown, re.MULTILINE)
    if m:
        return m.group(1).strip()
    stem = source_path.stem.replace("-", " ").replace("_", " ")
    return stem.title() if stem else source_path.name


def wrap_fragment_html(title: str, body_html: str) -> str:
    """Wrap an HTML fragment in a minimal HTML5 document."""
    safe_title = html.escape(title, quote=True)
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
