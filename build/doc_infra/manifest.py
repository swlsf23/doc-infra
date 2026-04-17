"""Parse manifest YAML and collect Markdown paths from nested ``sources`` trees."""

from __future__ import annotations

import copy
from pathlib import Path
from typing import Any

from ruamel.yaml import YAML

_yaml_safe = YAML(typ="safe")

FILES_KEY = "files"

DEFAULT_MANIFEST_VERSION = 1


def load_manifest_sources(manifest_path: Path) -> dict[str, Any]:
    """Load ``sources`` from a manifest file and normalize to compact form.

    Args:
        manifest_path: Path to ``manifest.yml``.

    Returns:
        Normalized ``sources`` mapping.

    Raises:
        FileNotFoundError: If the file does not exist.
        ValueError: If the document is invalid or has no ``sources`` key.
    """
    if not manifest_path.is_file():
        raise FileNotFoundError(f"Manifest not found: {manifest_path}")
    with manifest_path.open(encoding="utf-8") as f:
        data = _yaml_safe.load(f)
    if data is None or not isinstance(data, dict):
        raise ValueError(f"Manifest root must be a mapping: {manifest_path}")
    raw = data.get("sources")
    if raw is None:
        raise ValueError(f"Manifest has no 'sources' key: {manifest_path}")
    return normalize_sources_to_compact(raw)


def normalize_sources_to_compact(sources: Any) -> dict[str, Any]:
    """Normalize any supported legacy ``sources`` value into the compact nested form."""
    if isinstance(sources, list):
        return tree_from_flat_path_list(sources)
    if not isinstance(sources, dict):
        raise ValueError("sources must be a mapping or list")
    if FILES_KEY in sources:
        return _normalize_legacy_files_node(sources)
    return _normalize_compact_node(sources)


def _normalize_legacy_files_node(node: dict[str, Any]) -> dict[str, Any]:
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
    """Collect every Markdown path (POSIX, relative to content root)."""
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


def build_tree_from_disk(input_dir: Path) -> dict[str, Any]:
    """Build compact ``sources`` tree by walking ``input_dir`` for ``*.md`` files."""

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


def read_existing_sources_tree(manifest_path: Path) -> dict[str, Any]:
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
    tree = copy.deepcopy(existing)
    seen = collect_paths_from_tree(tree)
    for p in sorted(discovered_paths):
        if p not in seen:
            insert_path_parts(tree, p.split("/"))
            seen.add(p)
    return tree


def build_manifest_body(*, version: int, sources: dict[str, Any]) -> dict[str, Any]:
    return {
        "version": version,
        "generator": "doc-infra-generate-manifest",
        "sources": sources,
    }


def count_leaves(tree: dict[str, Any]) -> int:
    return len(collect_paths_from_tree(tree))
