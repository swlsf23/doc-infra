"""Build site navigation HTML from manifest ``sources`` trees."""

from __future__ import annotations

import html
import os
from pathlib import Path
from typing import Any

from doc_infra.manifest import FILES_KEY


def md_path_to_html_rel(md_rel: str) -> str:
    """``guides/foo.md`` -> ``guides/foo.html``."""
    if not md_rel.endswith(".md"):
        raise ValueError(f"expected .md path, got {md_rel!r}")
    return f"{md_rel[:-3]}.html"


def relative_href(from_page: str, to_page: str) -> str:
    """POSIX relative URL from one site output file to another (both paths relative to site root)."""
    start = Path(from_page).parent
    end = Path(to_page)
    return Path(os.path.relpath(end, start)).as_posix()


def _label_for_md_filename(filename: str) -> str:
    stem = filename[: -len(".md")] if filename.endswith(".md") else filename
    if stem == "index":
        return "Home"
    return stem.replace("-", " ").replace("_", " ").title()


def _branch_path_attr(prefix: tuple[str, ...], key: str) -> str:
    """Stable id for ``data-nav-path`` (folder segment or ``.md`` path with children)."""
    path = "/".join((*prefix, key))
    return html.escape(path, quote=True)


def _md_link_li(
    prefix: tuple[str, ...],
    key: str,
    *,
    from_html: str,
    current_md: str | None,
) -> str:
    """One ``<li>`` with a link to a markdown page (leaf)."""
    md_rel = "/".join((*prefix, key))
    html_rel = md_path_to_html_rel(md_rel)
    href = relative_href(from_html, html_rel)
    safe_href = html.escape(href, quote=True)
    label = html.escape(_label_for_md_filename(key))
    current_attr = (
        ' aria-current="page"' if current_md is not None and md_rel == current_md else ""
    )
    return f'<li><a href="{safe_href}"{current_attr}>{label}</a></li>'


def render_nav_html(
    sources: dict[str, Any],
    *,
    from_html: str,
    current_md: str | None = None,
    prefix: tuple[str, ...] = (),
) -> str:
    """Nested ``<ul>`` linking to every manifest page.

    ``from_html`` is the site-relative path of the page that will contain these links
    (e.g. ``reference/foo.html`` or root ``nav.html``), used for relative ``href`` values.

    If ``current_md`` is set (manifest path to ``.md``), that page gets ``aria-current="page"``.

    Key order follows the manifest mapping order (same as YAML after normalization).
    """
    items: list[str] = []
    for key, val in sources.items():
        if key == FILES_KEY:
            if not isinstance(val, list):
                continue
            for name in val:
                if isinstance(name, str) and name.endswith(".md"):
                    items.append(
                        _md_link_li(prefix, name, from_html=from_html, current_md=current_md)
                    )
            continue

        if key.endswith(".md"):
            if val is None or val == {}:
                items.append(_md_link_li(prefix, key, from_html=from_html, current_md=current_md))
            elif isinstance(val, dict):
                inner = render_nav_html(
                    val,
                    from_html=from_html,
                    current_md=current_md,
                    prefix=(*prefix, key),
                )
                md_rel = "/".join((*prefix, key))
                html_rel = md_path_to_html_rel(md_rel)
                href = relative_href(from_html, html_rel)
                safe_href = html.escape(href, quote=True)
                label = html.escape(_label_for_md_filename(key))
                current_attr = (
                    ' aria-current="page"'
                    if current_md is not None and md_rel == current_md
                    else ""
                )
                path_attr = _branch_path_attr(prefix, key)
                items.append(
                    f'<li class="doc-nav-branch">'
                    f'<details class="doc-nav-details" data-nav-path="{path_attr}">'
                    f'<summary class="doc-nav-summary">'
                    f'<a href="{safe_href}"{current_attr}>{label}</a>'
                    f"</summary>"
                    f"{inner}"
                    f"</details></li>"
                )
            else:
                continue
        elif isinstance(val, dict):
            inner = render_nav_html(
                val,
                from_html=from_html,
                current_md=current_md,
                prefix=(*prefix, key),
            )
            label = html.escape(key.replace("-", " ").replace("_", " ").title())
            path_attr = _branch_path_attr(prefix, key)
            items.append(
                f'<li class="doc-nav-branch">'
                f'<details class="doc-nav-details" data-nav-path="{path_attr}">'
                f'<summary class="doc-nav-summary">{label}</summary>'
                f"{inner}"
                f"</details></li>"
            )
        else:
            continue

    if not items:
        return ""
    inner = "\n".join(items)
    return f"<ul>\n{inner}\n</ul>"
