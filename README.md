# doc-infra

Static documentation **site generator** infrastructure: YAML-driven manifests, a Python build pipeline (materialize → convert → site build), and sample content for development.

## Repository layout

| Path | Purpose |
| --- | --- |
| [`code/`](code/) | Build tooling and [`code/config.yml`](code/config.yml) |
| [`code/generate_manifest.py`](code/generate_manifest.py) | Scans Markdown under `input_dir` and writes [`content/manifest.yml`](content/manifest.yml) |
| [`content/src/`](content/src/) | Example Markdown sources (replace with real docs over time) |
| [`content/manifest.yml`](content/manifest.yml) | Generated or hand-edited manifest (see script docstring for shape) |
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

### `code/config.yml`

- **`input_dir`** — Root to scan (absolute, or relative to the directory containing `config.yml`).
- **`manifest_path`** — Output manifest file (resolved the same way).
- **`on_existing_manifest`** — `overwrite` (replace), `stop` (error if file exists), or `append` (merge in new paths only).
- **`manifest_version`** (optional) — Integer written as `version` in the manifest (default `1`).

Full behavior and YAML examples are documented in the module docstring at the top of [`code/generate_manifest.py`](code/generate_manifest.py).

## Status

Early scaffolding: manifest generation and sample content are in place; the rest of the pipeline (HTML conversion, site build, link checking) is not implemented yet.
