r"""Convert Markdown listed in the manifest to HTML files.

Reads ``input_dir``, ``manifest_path``, ``html_output_dir``, ``converter``,
``markdown_directives`` (optional), and ``on_existing_html`` from ``config.yml``
(paths relative to the config file unless absolute).

``on_existing_html``:

- ``overwrite``: replace existing ``.html`` files (default).
- ``skip``: leave existing ``.html`` files unchanged. Only write missing outputs.
- ``stop``: if any target ``.html`` already exists, exit with an error and write
  nothing.

For each ``*.md`` path in the manifest, writes ``<same-relative-path>.html`` under
``html_output_dir``, using the configured :class:`~pipeline.converters.base.DocumentConverter`.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Any

from pipeline.config import CONFIG_NAME, load_config, resolve_path
from pipeline.converters.registry import get_converter
from pipeline.html import title_from_markdown_or_path, wrap_fragment_html
from pipeline.manifest import collect_paths_from_tree, load_manifest_sources


def md_to_html_path(rel_md: str) -> str:
    """Map ``guides/foo.md`` to ``guides/foo.html``."""
    if not rel_md.endswith(".md"):
        raise ValueError(f"expected .md path, got {rel_md!r}")
    return f"{rel_md[:-3]}.html"


def convert_all(
    *,
    input_dir: Path,
    manifest_path: Path,
    html_output_dir: Path,
    converter_name: str,
    on_existing_html: str = "overwrite",
    markdown_directives: bool = True,
) -> tuple[int, list[str], int]:
    """Convert every manifest page.

    Returns:
        Tuple of (files written, error messages, number of skipped paths when
        ``on_existing_html`` is ``skip`` and the target already exists).
    """
    if on_existing_html not in ("overwrite", "skip", "stop"):
        raise ValueError(
            "on_existing_html must be one of: overwrite, skip, stop",
        )

    sources = load_manifest_sources(manifest_path)
    paths = sorted(collect_paths_from_tree(sources))
    converter = get_converter(
        converter_name,
        directives_enabled=markdown_directives,
    )
    errors: list[str] = []
    skipped = 0

    if on_existing_html == "stop":
        collisions: list[str] = []
        for rel in paths:
            out_path = html_output_dir / md_to_html_path(rel)
            if out_path.is_file():
                collisions.append(str(out_path))
        if collisions:
            errors.append(
                "on_existing_html=stop: target HTML file(s) already exist; "
                "remove them or run with overwrite/skip. Examples:\n  "
                + "\n  ".join(collisions[:10])
                + (f"\n  ... and {len(collisions) - 10} more" if len(collisions) > 10 else "")
            )
            return 0, errors, 0

    n = 0
    for rel in paths:
        src = input_dir / rel
        if not src.is_file():
            errors.append(f"missing source file: {src} (manifest: {rel})")
            continue
        out_rel = md_to_html_path(rel)
        out_path = html_output_dir / out_rel
        if on_existing_html == "skip" and out_path.is_file():
            skipped += 1
            continue

        text = src.read_text(encoding="utf-8")
        try:
            fragment = converter.convert(text, source_path=src)
        except Exception as e:
            errors.append(f"{rel}: conversion failed: {e}")
            continue
        title = title_from_markdown_or_path(text, src)
        full_html = wrap_fragment_html(title, fragment)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(full_html, encoding="utf-8")
        n += 1
    return n, errors, skipped


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Convert Markdown from the manifest to HTML files.",
    )
    parser.add_argument(
        "--config",
        type=Path,
        default=None,
        help=f"Path to config.yml (default: {CONFIG_NAME} next to convert/)",
    )
    args = parser.parse_args()

    script_dir = Path(__file__).resolve().parent.parent
    config_path = args.config if args.config is not None else script_dir / CONFIG_NAME

    try:
        cfg: dict[str, Any] = load_config(config_path)
    except (OSError, ValueError) as e:
        print(f"error: {e}", file=sys.stderr)
        return 1

    config_dir = config_path.resolve().parent

    try:
        input_dir_s = cfg["input_dir"]
        manifest_path_s = cfg["manifest_path"]
        html_out_s = cfg["html_output_dir"]
        converter_name = cfg.get("converter", "markdown")
    except KeyError as e:
        print(f"error: missing config key: {e}", file=sys.stderr)
        return 1

    if not isinstance(converter_name, str):
        print("error: converter must be a string", file=sys.stderr)
        return 1

    on_existing_html = cfg.get("on_existing_html", "overwrite")
    if not isinstance(on_existing_html, str):
        print("error: on_existing_html must be a string", file=sys.stderr)
        return 1

    markdown_directives = cfg.get("markdown_directives", True)
    if not isinstance(markdown_directives, bool):
        print("error: markdown_directives must be a boolean (true/false)", file=sys.stderr)
        return 1

    input_dir = resolve_path(config_dir, str(input_dir_s))
    manifest_path = resolve_path(config_dir, str(manifest_path_s))
    html_output_dir = resolve_path(config_dir, str(html_out_s))

    try:
        n, errors, skipped = convert_all(
            input_dir=input_dir,
            manifest_path=manifest_path,
            html_output_dir=html_output_dir,
            converter_name=converter_name,
            on_existing_html=on_existing_html,
            markdown_directives=markdown_directives,
        )
    except (FileNotFoundError, ValueError) as e:
        print(f"error: {e}", file=sys.stderr)
        return 1
    except KeyError as e:
        print(f"error: {e}", file=sys.stderr)
        return 1

    for msg in errors:
        print(msg, file=sys.stderr)
    if skipped:
        print(
            f"Skipped {skipped} page(s) (target HTML already exists; on_existing_html=skip).",
            file=sys.stderr,
        )

    print(
        f"Converted {n} page(s) to {html_output_dir} "
        f"(converter={converter_name!r}, on_existing_html={on_existing_html!r}, "
        f"markdown_directives={markdown_directives!r})",
    )
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
