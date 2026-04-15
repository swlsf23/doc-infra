#!/usr/bin/env python3
"""CLI entry: convert manifest Markdown sources to HTML (see :mod:`doc_infra.convert`)."""

from __future__ import annotations

import sys
from pathlib import Path

_CODE_ROOT = Path(__file__).resolve().parent
if str(_CODE_ROOT) not in sys.path:
    sys.path.insert(0, str(_CODE_ROOT))

from doc_infra.convert import main

if __name__ == "__main__":
    raise SystemExit(main())
