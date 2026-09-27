#!/usr/bin/env bash
# Prepare a Flow release branch from one small release-notes file.
#
# The logic is the Flow program in scripts/tools/prepare_release. It runs
# scripts/sync_version.sh and scripts/check_changelog.sh itself.
#
# Usage:
#   ./scripts/prepare_release.sh --version X.Y.Z --release-date YYYY-MM-DD \
#       --notes .github/releases/X.Y.Z.md [--root DIR]

set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd -P)"

BIN="$ROOT/$("$ROOT/scripts/tools/build_tool.sh" prepare_release)"
PREPARE_RELEASE_ROOT="$ROOT" exec "$BIN" "$@"
