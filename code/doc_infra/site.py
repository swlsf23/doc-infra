"""Second build stage: wrap raw ``output/html`` pages with UX (navigation) into ``output/site``."""

from __future__ import annotations

import re
import shutil
from pathlib import Path
from typing import Any
from urllib.parse import quote

from doc_infra.manifest import collect_paths_from_tree, load_manifest_sources
from doc_infra.navigation import md_path_to_html_rel, relative_href, render_nav_html

# Single site-wide navigation document (iframe target); links use <base target="_parent">.
NAV_HTML = "nav.html"
# Site entry (home) in site output; must match manifest root index if present.
SITE_INDEX_HTML = "index.html"
# Used when ``site_github_url`` is omitted or blank in config. Set YAML ``site_github_url: false`` to hide.
DEFAULT_SITE_GITHUB_URL = "https://github.com/swlsf23/doc-infra"

# GitHub mark (16px), currentColor — matches pill buttons in ``ux/site.css``.
_GITHUB_ICON_SVG = (
    '<svg class="doc-header-github-icon" xmlns="http://www.w3.org/2000/svg" '
    'viewBox="0 0 16 16" width="16" height="16" fill="currentColor" aria-hidden="true">'
    '<path d="M8 0C3.58 0 0 3.58 0 8c0 3.54 2.29 6.53 5.47 7.59.4.07.55-.17.55-.38 0-.19-.01-.82-.01-1.49-2.01.37-2.53-.49-2.69-.94-.09-.23-.48-.94-.82-1.13-.28-.15-.68-.52-.01-.53.63-.01 1.08.58 1.23.82.72 1.21 1.87.87 2.33.66.07-.52.28-.87.51-1.07-1.78-.2-3.64-.89-3.64-3.95 0-.87.31-1.59.82-2.15-.08-.2-.36-1.02.08-2.12 0 0 .67-.21 2.2.82.64-.18 1.32-.27 2-.27.68 0 1.36.09 2 .27 1.53-1.04 2.2-.82 2.2-.82.44 1.1.16 1.92.08 2.12.51.56.82 1.27.82 2.15 0 3.07-1.87 3.75-3.65 3.95.29.25.54.73.54 1.48 0 1.07-.01 1.93-.01 2.2 0 .21.15.46.55.38A8.013 8.013 0 0016 8c0-4.42-3.58-8-8-8z"/>'
    "</svg>"
)


def resolve_site_github_url(value: Any) -> str | None:
    """Return repo URL for the header, or ``None`` to omit the GitHub control."""
    if value is False:
        return None
    if isinstance(value, str) and value.strip():
        return value.strip()
    return DEFAULT_SITE_GITHUB_URL

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


def wrap_nav_page(*, nav_inner_html: str, stylesheet_href: str) -> str:
    """Standalone ``nav.html``: full tree once. ``<base target="_parent">`` so links opened from an iframe replace the doc page, not the iframe.

    ``assets/nav.js`` restores scroll position and branch open state (``sessionStorage``) and expands branches along the current page path when ``?c=`` is present.
    """
    import html as html_module

    safe_href = html_module.escape(stylesheet_href, quote=True)
    safe_js = html_module.escape(relative_href(NAV_HTML, "assets/nav.js"), quote=True)
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Navigation</title>
  <base target="_parent">
  <link rel="stylesheet" href="{safe_href}">
</head>
<body class="doc-nav-body">
  <nav class="doc-nav" aria-label="Site">
{nav_inner_html}
  </nav>
  <script src="{safe_js}" defer></script>
</body>
</html>
"""


def _header_fragment(*, home_href: str, github_url: str | None) -> str:
    """Top utility bar: brand left, optional GitHub action right."""
    import html as html_module

    safe_home = html_module.escape(home_href, quote=True)
    brand_html = f'<a class="doc-brand" href="{safe_home}" aria-label="Go to docs home">Doc Infra</a>'
    prefix = home_href[: -len("index.html")] if home_href.endswith("index.html") else ""
    top_links = (
        ("Getting Started", f"{prefix}getting-started/overview.html"),
        ("Guides", f"{prefix}guides/pipeline-stages.html"),
        ("Reference", f"{prefix}reference/glossary.html"),
    )
    links_html = "".join(
        f'<a class="doc-header-link" href="{html_module.escape(href, quote=True)}">{html_module.escape(label)}</a>'
        for label, href in top_links
    )
    if github_url:
        gu = html_module.escape(github_url, quote=True)
        github_html = (
            f'<a class="doc-header-btn doc-header-btn--github" href="{gu}" '
            f'rel="noopener noreferrer" target="_blank">'
            f"{_GITHUB_ICON_SVG}"
            '<span class="doc-sr-only">GitHub</span></a>'
        )
        return f"""    <header class="doc-header">
      <div class="doc-header-start">
        {brand_html}
        <nav class="doc-header-links" aria-label="Top-level sections">
          {links_html}
        </nav>
      </div>
      <div class="doc-header-end" role="group" aria-label="Site actions">
        {github_html}
      </div>
    </header>
"""
    return f"""    <header class="doc-header">
      <div class="doc-header-start">
        {brand_html}
        <nav class="doc-header-links" aria-label="Top-level sections">
          {links_html}
        </nav>
      </div>
    </header>
"""


def _sidebar_nav_chrome_fragment() -> str:
    """Sidebar row: ←/→ toggle (left) + expand/collapse all +/− (right), above the nav iframe."""
    return """        <div class="doc-sidebar-toolbar">
          <label class="doc-header-btn doc-header-btn--toggle doc-nav-toggle-label">
            <input type="checkbox" class="doc-nav-toggle-input" aria-label="Show or hide sidebar navigation">
            <span class="doc-nav-toggle-text doc-nav-toggle-text--hide" aria-hidden="true">→</span>
            <span class="doc-nav-toggle-text doc-nav-toggle-text--show" aria-hidden="true">←</span>
          </label>
          <div class="doc-nav-toolbar" role="toolbar" aria-label="Section outline controls">
            <button type="button" class="doc-nav-toolbar-btn doc-nav-toolbar-btn--expand-toggle" id="doc-nav-expand-collapse-toggle" aria-pressed="false" title="Expand all sections" aria-label="Expand all sections">
              <span class="doc-nav-expand-collapse-icon doc-nav-expand-collapse-icon--expand" aria-hidden="true">+</span>
              <span class="doc-nav-expand-collapse-icon doc-nav-expand-collapse-icon--collapse" aria-hidden="true">−</span>
            </button>
          </div>
        </div>
"""


def wrap_site_page(
    *,
    title: str,
    body_html: str,
    nav_iframe_src: str,
    stylesheet_href: str,
    site_js_href: str,
    home_href: str,
    github_url: str | None,
) -> str:
    """Full HTML document for ``output/site`` with header, nav iframe, and ``<link>`` to ``site.css``.

    Navigation markup lives only in ``nav.html`` at site root; each page embeds a small iframe.

    All layout and typography live in ``ux/site.css`` (copied to ``assets/``). Use a local
    HTTP server from ``site_output_dir`` if ``file://`` does not load the stylesheet in
    your environment.
    """
    import html as html_module

    safe_title = html_module.escape(title, quote=True)
    safe_href = html_module.escape(stylesheet_href, quote=True)
    safe_nav_src = html_module.escape(nav_iframe_src, quote=True)
    safe_site_js = html_module.escape(site_js_href, quote=True)
    header_html = _header_fragment(home_href=home_href, github_url=github_url)
    sidebar_chrome_html = _sidebar_nav_chrome_fragment()
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{safe_title}</title>
  <link rel="stylesheet" href="{safe_href}">
</head>
<body>
  <div class="doc-root">
{header_html}
    <div class="doc-layout">
      <aside class="doc-sidebar">
{sidebar_chrome_html}
        <div class="doc-nav-frame" id="doc-nav-panel">
          <iframe class="doc-nav-iframe" title="Site navigation" src="{safe_nav_src}"></iframe>
        </div>
      </aside>
      <main class="doc-main">
{body_html}
      </main>
    </div>
  </div>
  <script src="{safe_site_js}" defer></script>
</body>
</html>
"""


def build_site(
    *,
    manifest_path: Path,
    html_output_dir: Path,
    site_output_dir: Path,
    ux_dir: Path,
    site_github_url: Any = None,
) -> tuple[int, list[str]]:
    """Build browsable site under ``site_output_dir``. Read raw HTML from ``html_output_dir``.

    Returns:
        (files_written, errors) where ``files_written`` is content pages plus ``nav.html`` (1 + page count).
    """
    errors: list[str] = []
    sources = load_manifest_sources(manifest_path)
    paths = sorted(collect_paths_from_tree(sources))
    resolved_github = resolve_site_github_url(site_github_url)

    try:
        copy_ux_assets(ux_dir, site_output_dir)
    except OSError as e:
        errors.append(f"ux assets: {e}")
        return 0, errors

    site_css_path = ux_dir / "site.css"
    nav_js_path = ux_dir / "nav.js"
    site_js_path = ux_dir / "site.js"
    if not site_css_path.is_file():
        errors.append(f"missing UX stylesheet: {site_css_path}")
        return 0, errors
    if not nav_js_path.is_file():
        errors.append(f"missing nav script: {nav_js_path}")
        return 0, errors
    if not site_js_path.is_file():
        errors.append(f"missing site script: {site_js_path}")
        return 0, errors

    nav_inner = render_nav_html(sources, from_html=NAV_HTML, current_md=None)
    nav_css_href = relative_href(NAV_HTML, "assets/site.css")
    nav_path = site_output_dir / NAV_HTML
    nav_path.write_text(
        wrap_nav_page(nav_inner_html=nav_inner, stylesheet_href=nav_css_href),
        encoding="utf-8",
    )

    n = 0
    for md_rel in paths:
        raw_rel = md_path_to_html_rel(md_rel)
        raw_path = html_output_dir / raw_rel
        if not raw_path.is_file():
            errors.append(f"missing raw HTML (run convert first): {raw_path} ({md_rel})")
            continue
        raw_html = raw_path.read_text(encoding="utf-8")
        title, body_inner = extract_title_and_body(raw_html)
        cur_html = md_path_to_html_rel(md_rel)
        css_href = relative_href(cur_html, "assets/site.css")
        site_js_href = relative_href(cur_html, "assets/site.js")
        nav_rel = relative_href(cur_html, NAV_HTML)
        nav_iframe_src = f"{nav_rel}?c={quote(md_rel, safe='')}"
        home_href = relative_href(cur_html, SITE_INDEX_HTML)
        page_html = wrap_site_page(
            title=title,
            body_html=body_inner,
            nav_iframe_src=nav_iframe_src,
            stylesheet_href=css_href,
            site_js_href=site_js_href,
            home_href=home_href,
            github_url=resolved_github,
        )
        out_path = site_output_dir / raw_rel
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(page_html, encoding="utf-8")
        n += 1

    return n + 1, errors
