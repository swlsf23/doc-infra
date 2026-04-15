# YAML keys (illustrative)

These keys are **not** authoritative until your schemas lock them in. They illustrate likely separation of concerns.

## `code/config.yml`

- `content_root`
- `output_dir`
- `manifest_path`
- `plugins`

## Manifest node (leaf)

- `source`
- `output`
- optional `converter`

## `site-config.yml`

- `title`
- `base_url`
- `theme` (if applicable)

Validate with a schema when you add one; until then, treat this page as documentation-only.
