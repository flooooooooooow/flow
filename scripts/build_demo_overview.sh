#!/usr/bin/env bash
# Generate docs/demos/overview.md from docs/demos/catalog.json.
#
# The generator is the Flow program in scripts/tools/demo_overview.
#
# Usage:
#   ./scripts/build_demo_overview.sh
#   ./scripts/build_demo_overview.sh --check [--check-previews]

set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

BIN="$(scripts/tools/build_tool.sh demo_overview)"
exec "$BIN" "$@"
