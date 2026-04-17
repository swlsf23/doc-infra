#!/usr/bin/env python3
"""Build the browsable site (navigation + UX assets) from raw HTML in ``html_output_dir``.

Run ``convert.py`` first so ``output/html`` exists. This stage writes to ``site_output_dir``
(typically ``output/site``) and copies static assets from ``ux_dir``.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Any

from doc_infra.config import CONFIG_NAME, load_config, resolve_path
from doc_infra.site import build_site


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Wrap raw HTML with nav and UX assets into the site output directory.",
    )
    parser.add_argument(
        "--config",
        type=Path,
        default=None,
        help=f"Path to config.yml (default: {CONFIG_NAME} next to build/)",
    )
    args = parser.parse_args()

    script_dir = Path(__file__).resolve().parent
    config_path = args.config if args.config is not None else script_dir / CONFIG_NAME

    try:
        cfg: dict[str, Any] = load_config(config_path)
    except (OSError, ValueError) as e:
        print(f"error: {e}", file=sys.stderr)
        return 1

    config_dir = config_path.resolve().parent

    try:
        manifest_path_s = cfg["manifest_path"]
        html_out_s = cfg["html_output_dir"]
        site_out_s = cfg["site_output_dir"]
        ux_dir_s = cfg["ux_dir"]
    except KeyError as e:
        print(f"error: missing config key: {e}", file=sys.stderr)
        return 1

    manifest_path = resolve_path(config_dir, str(manifest_path_s))
    html_output_dir = resolve_path(config_dir, str(html_out_s))
    site_output_dir = resolve_path(config_dir, str(site_out_s))
    ux_dir = resolve_path(config_dir, str(ux_dir_s))

    site_github_raw = cfg.get("site_github_url")
    if site_github_raw is not None and site_github_raw is not False and not isinstance(
        site_github_raw,
        str,
    ):
        print(
            "error: site_github_url must be a string, false, or omitted (see README)",
            file=sys.stderr,
        )
        return 1

    n, errors = build_site(
        manifest_path=manifest_path,
        html_output_dir=html_output_dir,
        site_output_dir=site_output_dir,
        ux_dir=ux_dir,
        site_github_url=site_github_raw,
    )

    for msg in errors:
        print(msg, file=sys.stderr)

    content_pages = max(0, n - 1)
    print(
        f"Built {content_pages} content page(s), nav.html, and assets in {site_output_dir} "
        f"(from raw HTML in {html_output_dir}, ux={ux_dir})",
    )
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
