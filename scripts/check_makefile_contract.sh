#!/usr/bin/env bash
# Keep the root Makefile a thin wrapper around ./flow (#974).
#
# The checker is the Flow program in scripts/tools/makefile_contract.
#
# Usage: ./scripts/check_makefile_contract.sh
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

BIN="$(scripts/tools/build_tool.sh makefile_contract)"
exec "$BIN" "$@"
