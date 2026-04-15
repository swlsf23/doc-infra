"""Abstract base for document converters."""

from __future__ import annotations

from abc import ABC, abstractmethod
from pathlib import Path


class DocumentConverter(ABC):
    """Turn source text (e.g. Markdown) into an HTML fragment."""

    @property
    @abstractmethod
    def id(self) -> str:
        """Stable id used in ``config.yml`` (e.g. ``markdown``)."""

    @abstractmethod
    def convert(self, text: str, *, source_path: Path | None = None) -> str:
        """Return HTML body fragment (no ``<html>`` wrapper)."""
