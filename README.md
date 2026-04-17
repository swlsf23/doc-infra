# doc-infra

Static documentation **site generator** infrastructure: YAML-driven manifests, a Python build pipeline (materialize → convert → site build), and sample content for development.

## Repository layout

| Path | Purpose |
| --- | --- |
| [`build/doc_infra/`](build/doc_infra/) | Python package: manifest parsing, converters, [`convert`](build/doc_infra/convert.py) CLI logic |
| [`build/config.yml`](build/config.yml) | Shared paths and options for scripts |
| [`build/generate_manifest.py`](build/generate_manifest.py) | Scans Markdown under `input_dir` and writes [`content/manifest.yml`](content/manifest.yml) |
| [`build/convert.py`](build/convert.py) | Stage 1: converts each manifest page from Markdown to **raw** HTML |
| [`build/build_site.py`](build/build_site.py) | Stage 2: wraps raw HTML with navigation and copies [`ux/`](ux/) assets into `site_output_dir` |
| [`ux/`](ux/) | UX static assets (`site.css`, `nav.js`, `site.js`, …) copied into the site output |
| [`content/src/`](content/src/) | Example Markdown sources (replace with real docs over time) |
| [`content/manifest.yml`](content/manifest.yml) | Generated or hand-edited manifest |
| [`output/html/`](output/html/) | Raw HTML from `convert.py` only (gitignored) |
| [`output/site/`](output/site/) | Browsable site from `build_site.py` (gitignored) |
| [`content/site-config.yml`](content/site-config.yml) | Site-wide settings for templates (not yet wired) |
| [`requirements.txt`](requirements.txt) | Python dependencies |

## Prerequisites

- Python 3.11+ (recommended)

## Setup

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Generate the manifest

The manifest lists what the site builds and in what order. The helper script discovers all `*.md` files under the configured `input_dir` and writes a nested YAML tree.

```bash
python build/generate_manifest.py
```

Optional: `python build/generate_manifest.py --config /path/to/config.yml`

## Convert Markdown to HTML

Uses the manifest and [`doc_infra.converters.registry`](build/doc_infra/converters/registry.py) (Markdown backend under [`markdown/mistune/`](build/doc_infra/converters/markdown/mistune)): default **`markdown`** is [Mistune](https://github.com/lepture/mistune) (pure Python). Each page becomes a minimal HTML5 document under `html_output_dir`, mirroring paths (`guides/foo.md` → `guides/foo.html`).

```bash
python build/convert.py
```

Optional: `python build/convert.py --config /path/to/config.yml`

**Admonitions** (styled callouts) use a fenced block: an opening line `::: caution` (or `warning`, `note`), an optional title on the same line, body text, then a closing `:::` on its own line. Body content supports **inline** Markdown (emphasis, links, code). See [`directives.py`](build/doc_infra/converters/markdown/mistune/directives.py).

## Build the browsable site (navigation)

After `convert.py`, run `build_site.py`. It reads raw HTML from `html_output_dir`, writes **`nav.html`** once at the site root (full manifest tree, shared by every page), wraps each page in a layout that loads that nav in an **iframe** (so nav markup is not duplicated in each HTML file), links [`ux/site.css`](ux/site.css) (copied to `assets/site.css`), and copies the rest of `ux/` into `site_output_dir/assets/`. Writes content pages under `site_output_dir` (default `output/site`). If styles do not load over `file://`, run `python -m http.server` from `output/site` and open **http://127.0.0.1:8000/** (or use an external browser).

```bash
python build/build_site.py
```

Optional: `python build/build_site.py --config /path/to/config.yml`

## `build/config.yml`

- **`input_dir`**: Root for Markdown sources (absolute, or relative to the directory containing `config.yml`).
- **`manifest_path`**: Manifest file (resolved the same way).
- **`html_output_dir`**: Where `convert.py` writes **raw** `.html` files.
- **`site_output_dir`**: Where `build_site.py` writes the **browsable** site (nav + UX).
- **`ux_dir`**: Directory of static assets (for example CSS) copied into `site_output_dir/assets/`.
- **`site_github_url`**: Header **GitHub** pill (icon + label). Use a quoted URL. If the key is omitted or set to an empty string, a **default** URL is used (`doc_infra.site.DEFAULT_SITE_GITHUB_URL`). Set to YAML **`false`** to hide the GitHub control.
- **`converter`**: Converter id (default `markdown`). Register new converters in [`build/doc_infra/converters/`](build/doc_infra/converters/).
- **`markdown_directives`**: Boolean (default `true`). When `true`, `::: caution` / `warning` / `note` … `:::` blocks become styled admonition HTML. When `false`, the Mistune directives plugin is off and `:::` lines are ordinary Markdown (they still convert to HTML as normal paragraph text).
- **`on_existing_html`**: `overwrite` (replace files), `skip` (only write missing `.html`), or `stop` (error if any target `.html` already exists. Writes nothing).
- **`on_existing_manifest`**: Used only by `generate_manifest.py`: `overwrite`, `stop`, or `append`.
- **`manifest_version`** (optional): Integer written as `version` in the manifest (default `1`).

Manifest shape and behavior are documented in [`build/doc_infra/manifest.py`](build/doc_infra/manifest.py) and the docstring at the top of [`build/generate_manifest.py`](build/generate_manifest.py).

## Status

Manifest generation, Markdown→HTML conversion (`output/html`), and a second-stage browsable site with navigation (`output/site` via `build_site.py` and `ux/`) are implemented. **[`release/publish-site.sh`](release/publish-site.sh)** builds **`output/site`**, **`aws s3 sync`** to your bucket prefix, and invalidates CloudFront. For day-to-day use, put **`export …`** lines in **`release/publish.local`** (gitignored); CI can set the same variables in the environment. Materialize stage, CI deploy, link checking, and wiring `site-config.yml` into the site are not implemented yet.

## Release notes

### v0.1.0

First usable baseline release:

- Markdown-to-HTML conversion via Mistune.
- Site build stage with shared navigation and UX assets.
- Styled `::: note|warning|caution` directives (configurable via `markdown_directives`).
- Sample content corpus with internal-testing notice blocks.
