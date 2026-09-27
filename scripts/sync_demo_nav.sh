#!/usr/bin/env bash
# Keep the Wiki's Demos tab in docs/nav.json aligned with
# docs/demos/catalog.json.
#
# The logic is the Flow program in scripts/tools/demo_nav.
#
# Usage:
#   ./scripts/sync_demo_nav.sh
#   ./scripts/sync_demo_nav.sh --check

set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

BIN="$(scripts/tools/build_tool.sh demo_nav)"
exec "$BIN" "$@"
