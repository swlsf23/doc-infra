"""Second build stage: wrap raw ``output/html`` pages with UX (navigation) into ``output/site``."""

from __future__ import annotations

import re
import shutil
from pathlib import Path
from typing import Any

from doc_infra.manifest import collect_paths_from_tree, load_manifest_sources
from doc_infra.navigation import md_path_to_html_rel, relative_href, render_nav_html

# Raw HTML from convert.py: minimal wrapper with <title> and <body>…</body>
_TITLE_RE = re.compile(r"<title>([^<]*)</title>", re.IGNORECASE | re.DOTALL)
_BODY_RE = re.compile(r"<body[^>]*>(.*)</body>", re.IGNORECASE | re.DOTALL)


def extract_title_and_body(raw_html: str) -> tuple[str, str]:
    """Parse title and inner HTML of ``body`` from convert output."""
    tm = _TITLE_RE.search(raw_html)
    title = (tm.group(1).strip() if tm else "") or "Untitled"
    bm = _BODY_RE.search(raw_html)
    body_inner = (bm.group(1).strip() if bm else "")
    return title, body_inner


def copy_ux_assets(ux_dir: Path, site_output_dir: Path) -> None:
    """Copy files from ``ux_dir`` into ``site_output_dir/assets/``."""
    if not ux_dir.is_dir():
        raise FileNotFoundError(f"ux_dir is not a directory: {ux_dir}")
    assets = site_output_dir / "assets"
    assets.mkdir(parents=True, exist_ok=True)
    for p in sorted(ux_dir.iterdir()):
        if p.is_file():
            shutil.copy2(p, assets / p.name)


def wrap_site_page(
    *,
    title: str,
    body_html: str,
    nav_html: str,
    stylesheet_href: str,
) -> str:
    """Full HTML document for ``output/site`` with nav and a single ``<link>`` to ``site.css``.

    All layout and typography live in ``ux/site.css`` (copied to ``assets/``). Use a local
    HTTP server from ``site_output_dir`` if ``file://`` does not load the stylesheet in
    your environment.
    """
    import html as html_module

    safe_title = html_module.escape(title, quote=True)
    safe_href = html_module.escape(stylesheet_href, quote=True)
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{safe_title}</title>
  <link rel="stylesheet" href="{safe_href}">
</head>
<body>
  <div class="doc-layout">
    <nav class="doc-nav" aria-label="Site">
{nav_html}
    </nav>
    <main class="doc-main">
{body_html}
    </main>
  </div>
</body>
</html>
"""


def build_site(
    *,
    manifest_path: Path,
    html_output_dir: Path,
    site_output_dir: Path,
    ux_dir: Path,
) -> tuple[int, list[str]]:
    """Build browsable site under ``site_output_dir``. Read raw HTML from ``html_output_dir``.

    Returns:
        (files_written, errors)
    """
    errors: list[str] = []
    sources = load_manifest_sources(manifest_path)
    paths = sorted(collect_paths_from_tree(sources))

    try:
        copy_ux_assets(ux_dir, site_output_dir)
    except OSError as e:
        errors.append(f"ux assets: {e}")
        return 0, errors

    site_css_path = ux_dir / "site.css"
    if not site_css_path.is_file():
        errors.append(f"missing UX stylesheet: {site_css_path}")
        return 0, errors

    n = 0
    for md_rel in paths:
        raw_rel = md_path_to_html_rel(md_rel)
        raw_path = html_output_dir / raw_rel
        if not raw_path.is_file():
            errors.append(f"missing raw HTML (run convert first): {raw_path} ({md_rel})")
            continue
        raw_html = raw_path.read_text(encoding="utf-8")
        title, body_inner = extract_title_and_body(raw_html)
        nav_html = render_nav_html(sources, current_md=md_rel)
        cur_html = md_path_to_html_rel(md_rel)
        css_href = relative_href(cur_html, "assets/site.css")
        page_html = wrap_site_page(
            title=title,
            body_html=body_inner,
            nav_html=nav_html,
            stylesheet_href=css_href,
        )
        out_path = site_output_dir / raw_rel
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(page_html, encoding="utf-8")
        n += 1

    return n, errors
