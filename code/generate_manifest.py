#!/usr/bin/env python3
r"""Scan Markdown under a configured input directory and write ``manifest.yml``.

Configuration is read from ``config.yml`` in the same directory as this script
(unless ``--config`` is passed). Expected keys:

``input_dir`` (str)
    Root directory to scan for ``*.md`` files. May be absolute or relative;
    relative paths are resolved against the **directory containing** ``config.yml``.

``manifest_path`` (str)
    Destination YAML file for the generated manifest. Resolved the same way as
    ``input_dir``.

``on_existing_manifest`` (str)
    One of:

    - ``overwrite`` — Replace the manifest with a fresh tree from disk (default
      for regeneration).
    - ``stop`` — If ``manifest_path`` already exists, exit with an error and do
      not write.
    - ``append`` — Keep existing sources and add any ``.md`` paths found on disk
      that are not already represented (after normalizing legacy shapes).

``manifest_version`` (int, optional)
    Written as top-level ``version`` in the output file. Defaults to ``1``.

**Output shape (``sources``):** nested mappings mirroring subdirectories; each
Markdown file is a leaf key ending in ``.md`` with a null value. Legacy
manifests using ``files:`` lists or a flat ``[{path: ...}, ...]`` list are
still **read** and normalized internally.

Example (generated):

.. code-block:: yaml

   getting-started:
     overview.md:
     subdir:
       page.md:

Optional manual TOC nesting (children resolve as **sibling** paths in the same
folder as the parent ``.md``):

.. code-block:: yaml

   getting-started:
     config-basics.md:
       config-basics-start.md:
     first-build.md:
"""

from __future__ import annotations

import argparse
import copy
import sys
from pathlib import Path
from typing import Any

from ruamel.yaml import YAML

# Default name when --config is not used (resolved next to this file).
CONFIG_NAME = "config.yml"

# Safe loader for config and existing manifests; writer tuned for readable nesting.
_yaml_safe = YAML(typ="safe")
_yaml_out = YAML()
_yaml_out.default_flow_style = False
_yaml_out.allow_unicode = True
_yaml_out.indent(mapping=2, sequence=4, offset=2)

DEFAULT_MANIFEST_VERSION = 1

# Older generated manifests used a ``files: [foo.md, ...]`` key per directory.
FILES_KEY = "files"


def load_config(path: Path) -> dict[str, Any]:
    """Load and validate ``config.yml``.

    Args:
        path: Path to the YAML config file.

    Returns:
        The top-level mapping from the file.

    Raises:
        FileNotFoundError: If ``path`` does not exist.
        ValueError: If the document is not a YAML mapping.
    """
    if not path.is_file():
        raise FileNotFoundError(f"Config not found: {path}")
    with path.open(encoding="utf-8") as f:
        data = _yaml_safe.load(f)
    if not isinstance(data, dict):
        raise ValueError(f"Config root must be a mapping: {path}")
    return data


def resolve_path(base_dir: Path, value: str) -> Path:
    """Resolve a config path: absolute paths stay absolute; others are relative to ``base_dir``."""
    p = Path(value)
    if p.is_absolute():
        return p.resolve()
    return (base_dir / p).resolve()


def build_tree_from_disk(input_dir: Path) -> dict[str, Any]:
    """Build the compact ``sources`` tree by walking ``input_dir``.

    Each ``*.md`` file in a directory becomes ``filename.md: null`` at that
    level; each subdirectory becomes a nested mapping. Empty directories are
    omitted.

    Args:
        input_dir: Content root (must exist and be a directory).

    Returns:
        Nested dict suitable for the manifest ``sources`` key.

    Raises:
        NotADirectoryError: If ``input_dir`` is not a directory.
    """

    def walk(d: Path) -> dict[str, Any]:
        node: dict[str, Any] = {}
        files = sorted(
            p.name
            for p in d.iterdir()
            if p.is_file() and p.suffix.lower() == ".md"
        )
        subs = sorted(p for p in d.iterdir() if p.is_dir())
        for name in files:
            node[name] = None
        for sub in subs:
            child = walk(sub)
            if child:
                node[sub.name] = child
        return node

    if not input_dir.is_dir():
        raise NotADirectoryError(f"input_dir is not a directory: {input_dir}")
    return walk(input_dir)


def normalize_sources_to_compact(sources: Any) -> dict[str, Any]:
    """Normalize any supported legacy ``sources`` value into the compact nested form.

    Args:
        sources: Either a mapping (compact or legacy ``files:`` style) or a
            legacy list of ``{"path": "a/b.md"}`` objects.

    Returns:
        A nested dict using only compact conventions (``*.md`` leaves, folder
        keys without ``.md``).

    Raises:
        ValueError: If the structure cannot be interpreted.
    """
    if isinstance(sources, list):
        return tree_from_flat_path_list(sources)
    if not isinstance(sources, dict):
        raise ValueError("sources must be a mapping or list")
    if FILES_KEY in sources:
        return _normalize_legacy_files_node(sources)
    return _normalize_compact_node(sources)


def _normalize_legacy_files_node(node: dict[str, Any]) -> dict[str, Any]:
    """Convert one legacy node that may contain ``files:`` plus subdirectories."""
    out: dict[str, Any] = {}
    raw_files = node.get(FILES_KEY, [])
    if not isinstance(raw_files, list):
        raise ValueError(f"'{FILES_KEY}' must be a list")
    for name in raw_files:
        if not isinstance(name, str):
            raise ValueError("file name must be a string")
        out[name] = None
    for key, val in node.items():
        if key == FILES_KEY:
            continue
        if not isinstance(val, dict):
            raise ValueError(f"directory {key!r} must be a mapping")
        out[key] = normalize_sources_to_compact(val)
    return out


def _normalize_compact_node(node: dict[str, Any]) -> dict[str, Any]:
    """Validate and copy a compact subtree, recursing into directories and nested TOC groups."""
    out: dict[str, Any] = {}
    for key, val in node.items():
        if key.endswith(".md"):
            if val is None or val == {}:
                out[key] = None
            elif isinstance(val, dict):
                out[key] = _normalize_compact_node(val)
            else:
                raise ValueError(f"invalid value for {key!r}: expected null or mapping")
        else:
            if not isinstance(val, dict):
                raise ValueError(f"directory {key!r} must be a mapping")
            out[key] = normalize_sources_to_compact(val)
    return out


def collect_paths_from_tree(tree: dict[str, Any], prefix: tuple[str, ...] = ()) -> set[str]:
    """Collect every Markdown path represented by a ``sources`` subtree.

    Supports legacy ``files:`` nodes, compact leaves, and optional nesting
    under a ``*.md`` key (sibling paths in the same directory as that file).

    Args:
        tree: A ``sources`` mapping (or legacy node containing ``files``).
        prefix: Path segments from the content root to this node (POSIX).

    Returns:
        Set of slash-separated paths ending in ``.md``, relative to the content root.

    Raises:
        ValueError: On malformed nodes.
    """
    out: set[str] = set()
    files = tree.get(FILES_KEY)
    if files is not None:
        if not isinstance(files, list):
            raise ValueError(f"'{FILES_KEY}' must be a list, got {type(files)}")
        for name in files:
            if not isinstance(name, str):
                raise ValueError("file entry must be a string")
            out.add("/".join((*prefix, name)))
        for key, val in tree.items():
            if key == FILES_KEY:
                continue
            if not isinstance(val, dict):
                raise ValueError(f"directory node {key!r} must be a mapping")
            out |= collect_paths_from_tree(val, (*prefix, key))
        return out

    for key, val in tree.items():
        if key.endswith(".md"):
            if val is None:
                out.add("/".join((*prefix, key)))
            elif isinstance(val, dict):
                out.add("/".join((*prefix, key)))
                out |= _paths_nested_under_page(val, prefix)
            else:
                raise ValueError(f"invalid value under {key!r}")
        else:
            if not isinstance(val, dict):
                raise ValueError(f"directory node {key!r} must be a mapping")
            out |= collect_paths_from_tree(val, (*prefix, key))
    return out


def _paths_nested_under_page(
    node: dict[str, Any], parent_dir_prefix: tuple[str, ...]
) -> set[str]:
    """Resolve paths for keys nested under a ``*.md`` parent (TOC grouping).

    Child ``*.md`` keys contribute paths as siblings inside ``parent_dir_prefix``,
    not under a subdirectory named after the parent file.
    """
    out: set[str] = set()
    for ck, cv in node.items():
        if ck.endswith(".md"):
            if cv is None or cv == {}:
                out.add("/".join((*parent_dir_prefix, ck)))
            elif isinstance(cv, dict):
                out.add("/".join((*parent_dir_prefix, ck)))
                out |= _paths_nested_under_page(cv, parent_dir_prefix)
            else:
                raise ValueError(f"invalid value under {ck!r}")
        else:
            if not isinstance(cv, dict):
                raise ValueError(f"directory node {ck!r} must be a mapping")
            out |= collect_paths_from_tree(cv, (*parent_dir_prefix, ck))
    return out


def tree_from_flat_path_list(entries: list[dict[str, Any]]) -> dict[str, Any]:
    """Convert legacy ``[{path: "a/b.md"}, ...]`` into a compact nested tree."""
    tree: dict[str, Any] = {}
    for item in entries:
        if not isinstance(item, dict) or "path" not in item:
            raise ValueError("legacy list entries must be objects with 'path'")
        p = item["path"]
        if not isinstance(p, str):
            raise ValueError("path must be a string")
        insert_path_parts(tree, p.split("/"))
    return tree


def insert_path_parts(tree: dict[str, Any], parts: list[str]) -> None:
    """Insert a single POSIX path (split on ``/``) into a compact tree in place.

    Args:
        tree: Target subtree.
        parts: Path segments relative to the content root; the last segment must
            end with ``.md``. Directory segments must not end with ``.md``.

    Raises:
        ValueError: On invalid segments or conflicting structure.
    """
    if not parts:
        return
    if len(parts) == 1:
        name = parts[0]
        if not name.endswith(".md"):
            raise ValueError(f"expected a .md file, got {name!r}")
        tree[name] = None
        return
    head, *rest = parts
    if head.endswith(".md"):
        raise ValueError(f"cannot traverse past file segment {head!r}")
    child = tree.setdefault(head, {})
    if not isinstance(child, dict):
        raise ValueError(f"cannot add under {head!r}: not a mapping")
    insert_path_parts(child, rest)


def read_existing_sources_tree(manifest_path: Path) -> dict[str, Any]:
    """Load ``sources`` from an existing manifest and normalize to compact form.

    Args:
        manifest_path: Path to ``manifest.yml`` (may be missing or empty).

    Returns:
        Normalized ``sources`` dict, or an empty dict if the file is missing or
        has no ``sources`` key.

    Raises:
        ValueError: If the YAML root or ``sources`` shape is invalid.
    """
    if not manifest_path.is_file() or manifest_path.stat().st_size == 0:
        return {}
    with manifest_path.open(encoding="utf-8") as f:
        data = _yaml_safe.load(f)
    if data is None:
        return {}
    if not isinstance(data, dict):
        raise ValueError(f"Manifest root must be a mapping: {manifest_path}")
    raw = data.get("sources")
    if raw is None:
        return {}
    return normalize_sources_to_compact(raw)


def merge_append_tree(existing: dict[str, Any], discovered_paths: list[str]) -> dict[str, Any]:
    """Return a copy of ``existing`` with any missing ``discovered_paths`` inserted.

    Paths already present (after normalization) are left unchanged; new paths are
    merged using :func:`insert_path_parts`.
    """
    tree = copy.deepcopy(existing)
    seen = collect_paths_from_tree(tree)
    for p in sorted(discovered_paths):
        if p not in seen:
            insert_path_parts(tree, p.split("/"))
            seen.add(p)
    return tree


def build_manifest_body(*, version: int, sources: dict[str, Any]) -> dict[str, Any]:
    """Build the top-level YAML document written to ``manifest_path``."""
    return {
        "version": version,
        "generator": "doc-infra-generate-manifest",
        "sources": sources,
    }


def count_leaves(tree: dict[str, Any]) -> int:
    """Return how many distinct ``*.md`` paths are represented in ``tree``."""
    return len(collect_paths_from_tree(tree))


def main() -> int:
    """CLI entry: load config, apply ``on_existing_manifest`` rules, write YAML.

    Returns:
        Process exit code (``0`` on success, ``1`` on user-facing errors).
    """
    parser = argparse.ArgumentParser(
        description="Generate manifest.yml from config.yml and Markdown under input_dir."
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
