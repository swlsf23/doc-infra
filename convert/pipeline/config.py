"""Load ``config.yml`` and resolve paths relative to its directory."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from ruamel.yaml import YAML

CONFIG_NAME = "config.yml"

_yaml_safe = YAML(typ="safe")


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
