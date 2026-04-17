#!/usr/bin/env bash
# Build, upload, invalidate.
#
# Local machine: create release/publish.local (gitignored) once, for example:
#   export SITE_S3_BUCKET=sleslie-doc-infra-spa
#   export CLOUDFRONT_DISTRIBUTION_ID=E...
#   export SITE_S3_PREFIX=doc-infra
#   export AWS_PROFILE=...
#   export AWS_SSO_SESSION=portfolio   # optional; if set, runs: aws sso login --sso-session … before sync
# Then: ./release/publish-site.sh
#
# CI or one-off: set the same variables in the environment instead of publish.local.
# Optional: ./release/publish-site.sh --delete

set -euo pipefail

RELEASE_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT="$(cd "$RELEASE_DIR/.." && pwd)"
cd "$ROOT"

if [[ -f "$RELEASE_DIR/publish.local" ]]; then
	# shellcheck disable=SC1091
	source "$RELEASE_DIR/publish.local"
fi

: "${SITE_S3_BUCKET:?Set SITE_S3_BUCKET (release/publish.local or env)}"
: "${CLOUDFRONT_DISTRIBUTION_ID:?Set CLOUDFRONT_DISTRIBUTION_ID (release/publish.local or env)}"

PREFIX="${SITE_S3_PREFIX:-doc-infra}"
PREFIX="${PREFIX#/}"
S3_URI="s3://${SITE_S3_BUCKET}/${PREFIX}/"
INVALIDATION="/${PREFIX}/*"

PYTHON=(python3)
[[ -x "$ROOT/.venv/bin/python" ]] && PYTHON=("$ROOT/.venv/bin/python")

"${PYTHON[@]}" build/generate_manifest.py
"${PYTHON[@]}" build/convert.py
"${PYTHON[@]}" build/build_site.py

if [[ -n "${AWS_SSO_SESSION:-}" ]]; then
	aws sso login --sso-session "$AWS_SSO_SESSION"
fi

if [[ "${1:-}" == "--delete" ]]; then
	aws s3 sync "$ROOT/output/site" "$S3_URI" --delete
else
	aws s3 sync "$ROOT/output/site" "$S3_URI"
fi

aws cloudfront create-invalidation \
	--distribution-id "$CLOUDFRONT_DISTRIBUTION_ID" \
	--paths "$INVALIDATION" \
	--output text \
	--query 'Invalidation.Id'

echo "Synced to $S3_URI; invalidation $INVALIDATION"
