#!/usr/bin/env bash
# Open a Jules session for every open issue that does not already have one.
#
# The logic is the Flow program in scripts/tools/jules_dispatch. It runs
# `gh` and `jules` itself and keeps its state in jules_dispatch_state.json
# in the current directory.
#
# Usage:
#   ./scripts/dispatch_uncovered_jules.sh

set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd -P)"
BIN="$ROOT/$("$ROOT/scripts/tools/build_tool.sh" jules_dispatch)"
exec "$BIN" "$@"
