# doc-infra

Static documentation **site generator** infrastructure: YAML-driven manifests, a Python build pipeline (materialize → convert → site build), and sample content for development.

## Repository layout

| Path | Purpose |
| --- | --- |
| [`code/doc_infra/`](code/doc_infra/) | Python package: manifest parsing, converters, [`convert`](code/doc_infra/convert.py) CLI logic |
| [`code/config.yml`](code/config.yml) | Shared paths and options for scripts |
| [`code/generate_manifest.py`](code/generate_manifest.py) | Scans Markdown under `input_dir` and writes [`content/manifest.yml`](content/manifest.yml) |
| [`code/convert.py`](code/convert.py) | Converts each manifest page from Markdown to HTML |
| [`content/src/`](content/src/) | Example Markdown sources (replace with real docs over time) |
| [`content/manifest.yml`](content/manifest.yml) | Generated or hand-edited manifest |
| [`output/html/`](output/html/) | HTML output from `convert.py` (gitignored for now; may be committed later as published site docs) |
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
python code/generate_manifest.py
```

Optional: `python code/generate_manifest.py --config /path/to/config.yml`

## Convert Markdown to HTML

Uses the manifest and [`doc_infra.converters.registry`](code/doc_infra/converters/registry.py) (Markdown backend under [`markdown/mistune/`](code/doc_infra/converters/markdown/mistune)): default **`markdown`** is [Mistune](https://github.com/lepture/mistune) (pure Python). Each page becomes a minimal HTML5 document under `html_output_dir`, mirroring paths (`guides/foo.md` → `guides/foo.html`).

```bash
python code/convert.py
```

Optional: `python code/convert.py --config /path/to/config.yml`

## `code/config.yml`

- **`input_dir`** — Root for Markdown sources (absolute, or relative to the directory containing `config.yml`).
- **`manifest_path`** — Manifest file (resolved the same way).
- **`html_output_dir`** — Where `convert.py` writes `.html` files.
- **`converter`** — Converter id (default `markdown`). Register new converters in [`code/doc_infra/converters/`](code/doc_infra/converters/).
- **`on_existing_html`** — `overwrite` (replace files), `skip` (only write missing `.html`), or `stop` (error if any target `.html` already exists; writes nothing).
- **`on_existing_manifest`** — Used only by `generate_manifest.py`: `overwrite`, `stop`, or `append`.
- **`manifest_version`** (optional) — Integer written as `version` in the manifest (default `1`).

Manifest shape and behavior are documented in [`code/doc_infra/manifest.py`](code/doc_infra/manifest.py) and the docstring at the top of [`code/generate_manifest.py`](code/generate_manifest.py).

## Status

Manifest generation and Markdown→HTML conversion are implemented. Materialize stage, full site build, link checking, and wiring `site-config.yml` are not implemented yet.
