#!/usr/bin/env bash
# Check that the current release has a section in docs/project/CHANGELOG.md.
#
# The checker is the Flow program in scripts/tools/changelog_check.
#
# Usage:
#   ./scripts/check_changelog.sh

set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

BIN="$(scripts/tools/build_tool.sh changelog_check)"
exec "$BIN" "$@"
