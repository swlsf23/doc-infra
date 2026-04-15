"""Document converters (Markdown, etc.) registered by id."""

from __future__ import annotations

from doc_infra.converters.base import DocumentConverter

_CONVERTERS: dict[str, type[DocumentConverter]] = {}


def register_converter(name: str, cls: type[DocumentConverter]) -> None:
    _CONVERTERS[name] = cls


def get_converter(name: str) -> DocumentConverter:
    """Return a new converter instance for ``name``."""
    try:
        cls = _CONVERTERS[name]
    except KeyError as e:
        raise KeyError(
            f"unknown converter: {name!r} (available: {sorted(_CONVERTERS)})"
        ) from e
    return cls()


def registered_converter_ids() -> tuple[str, ...]:
    return tuple(sorted(_CONVERTERS))


def _load_builtin_converters() -> None:
    from doc_infra.converters.markdown.mistune.mistune import MistuneMarkdownConverter

    register_converter("markdown", MistuneMarkdownConverter)


_load_builtin_converters()
