#!/usr/bin/env bash
# Binary size report for compiled Flow programs.
#
#   scripts/tools/measure_size/measure_size.sh [--out report.md] [program.flow ...]
#
# Runs from the repository root, so program paths are relative to it.
# FLOW_HOST picks the compiler host (default flowc).

set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../../.." && pwd)"
cd "$ROOT"
BIN="$(scripts/tools/build_tool.sh measure_size)"
exec "$ROOT/$BIN" "$@"
