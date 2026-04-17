"""Abstract base for pluggable document converters.

Concrete implementations live under ``doc_infra.converters`` (e.g. Markdown
backends) and are registered in :mod:`doc_infra.converters.registry`.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from pathlib import Path


class DocumentConverter(ABC):
    """Convert one source document’s text into an HTML **fragment**.

    Subclass this type. Do not instantiate ``DocumentConverter`` itself.
    The build pipeline reads a page file, calls :meth:`convert`, then wraps
    the returned markup in a minimal HTML5 document (see :mod:`doc_infra.html`).
    """

    @property
    @abstractmethod
    def id(self) -> str:
        """Registry and config key for this converter (e.g. ``markdown``).

        Must match the ``converter`` value in ``config.yml`` and stay stable
        across releases for the same backend.
        """

    @abstractmethod
    def convert(self, text: str, *, source_path: Path | None = None) -> str:
        """Parse ``text`` and return **body-only** HTML (no ``<html>`` / ``<head>``).

        ``source_path`` is the path to the source file on disk when known.
        Backends may use it for path-sensitive behavior or ignore it.
        """
