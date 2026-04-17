"""Raw HTML converter for fixture ingestion.

This stage intentionally keeps behavior minimal for staged rollout:
it returns source text as-is, and lets later normalization enforce
canonical output structure.
"""

from __future__ import annotations

from pathlib import Path

from pipeline.converters.base import DocumentConverter


class IdentityHtmlConverter(DocumentConverter):
    """Pass through raw HTML content without modification."""

    @property
    def id(self) -> str:
        return "html"

    def convert(self, text: str, *, source_path: Path | None = None) -> str:
        return text
