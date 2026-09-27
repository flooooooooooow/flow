#!/usr/bin/env bash
# Validate stability/surfaces.json, the 1.0 stability surface manifest.
#
# The checker is the Flow program in scripts/tools/stability_manifest.
#
# Usage:
#   ./scripts/check_stability_manifest.sh
#   ./scripts/check_stability_manifest.sh --require-complete   # RC1 gate

set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

BIN="$(scripts/tools/build_tool.sh stability_manifest)"
exec "$BIN" "$@"
