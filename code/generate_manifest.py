#!/usr/bin/env python3
r"""Scan Markdown under a configured input directory and write ``manifest.yml``.

See :mod:`doc_infra.manifest` for the ``sources`` tree format and
:mod:`doc_infra.config` for path resolution.

Configuration keys are documented in the original module text below.

``input_dir`` (str)
    Root directory to scan for ``*.md`` files. May be absolute or relative;
    relative paths are resolved against the **directory containing** ``config.yml``.

``manifest_path`` (str)
    Destination YAML file for the generated manifest. Resolved the same way as
    ``input_dir``.

``on_existing_manifest`` (str)
    One of ``overwrite``, ``stop``, or ``append`` (see :func:`doc_infra.manifest.merge_append_tree`).

``manifest_version`` (int, optional)
    Written as top-level ``version`` in the output file. Defaults to ``1``.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

# Running as ``python code/generate_manifest.py`` puts ``code/`` on ``sys.path``.
_CODE_ROOT = Path(__file__).resolve().parent
if str(_CODE_ROOT) not in sys.path:
    sys.path.insert(0, str(_CODE_ROOT))

from ruamel.yaml import YAML

from doc_infra.config import CONFIG_NAME, load_config, resolve_path
from doc_infra.manifest import (
    DEFAULT_MANIFEST_VERSION,
    build_manifest_body,
    build_tree_from_disk,
    count_leaves,
    merge_append_tree,
    read_existing_sources_tree,
)

_yaml_out = YAML()
_yaml_out.default_flow_style = False
_yaml_out.allow_unicode = True
_yaml_out.indent(mapping=2, sequence=4, offset=2)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Generate manifest.yml from config.yml and Markdown under input_dir.",
    )
    parser.add_argument(
        "--config",
        type=Path,
        default=None,
        help="Path to config.yml (default: config.yml next to this script)",
    )
    args = parser.parse_args()

    script_dir = Path(__file__).resolve().parent
    config_path = args.config if args.config is not None else script_dir / CONFIG_NAME

    try:
        cfg = load_config(config_path)
    except (OSError, ValueError) as e:
        print(f"error: {e}", file=sys.stderr)
        return 1

    config_dir = config_path.resolve().parent

    try:
        input_dir_s = cfg["input_dir"]
        manifest_path_s = cfg["manifest_path"]
        behavior = cfg["on_existing_manifest"]
    except KeyError as e:
        print(f"error: missing config key: {e}", file=sys.stderr)
        return 1

    if behavior not in ("overwrite", "stop", "append"):
        print(
            "error: on_existing_manifest must be one of: overwrite, stop, append",
            file=sys.stderr,
        )
        return 1

    input_dir = resolve_path(config_dir, str(input_dir_s))
    manifest_path = resolve_path(config_dir, str(manifest_path_s))

    try:
        discovered = sorted(
            f.relative_to(input_dir).as_posix()
            for f in input_dir.rglob("*.md")
            if f.is_file()
        )
    except NotADirectoryError as e:
        print(f"error: {e}", file=sys.stderr)
        return 1

    if manifest_path.exists() and manifest_path.is_file():
        if behavior == "stop":
            print(
                f"error: manifest already exists (on_existing_manifest=stop): {manifest_path}",
                file=sys.stderr,
            )
            return 1
        if behavior == "append":
            try:
                existing = read_existing_sources_tree(manifest_path)
            except ValueError as e:
                print(f"error: {e}", file=sys.stderr)
                return 1
            sources = merge_append_tree(existing, discovered)
        else:
            sources = build_tree_from_disk(input_dir)
    else:
        sources = build_tree_from_disk(input_dir)

    version = cfg.get("manifest_version", DEFAULT_MANIFEST_VERSION)
    if not isinstance(version, int):
        print("error: manifest_version must be an integer", file=sys.stderr)
        return 1

    body = build_manifest_body(version=version, sources=sources)
    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    with manifest_path.open("w", encoding="utf-8") as f:
        _yaml_out.dump(body, f)

    n = count_leaves(sources)
    print(f"Wrote {manifest_path} ({n} markdown file(s)), input_dir={input_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
