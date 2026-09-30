#!/usr/bin/env bash
# Fail when tracked Python grows. New code in this repository is written in Flow.
#
# The ratchet logic is the Flow program in tools/python_ratchet. Flow cannot
# spawn processes yet, so git runs here and leaves the file list in
# build/python-ratchet/ for the Flow program to read. The program is built
# with the checked-in Stage-A bootstrap, so this check needs no Python.
#
# Usage:
#   ./scripts/python_ratchet.sh            check, exit 1 on new or grown Python
#   ./scripts/python_ratchet.sh --update   tighten the baseline after a port

set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

OUT=build/python-ratchet
mkdir -p "$OUT"

# Excluded, and nothing else may be:
#   third_party/, .lake/          vendored trees, which other projects own.
#   benchmarks/baselines/python/  benchmark subjects. They exist to measure
#                                 CPython and NumPy as a comparison baseline,
#                                 so they have to be Python. The harnesses
#                                 that run them are Flow and bash; no tooling
#                                 lives here.
#   examples/interop/python/      the Python side of Flow calling Python
#                                 (lib/stdlib/python_embed.flow, natively and
#                                 in Pyodide). The demo's subject is Python.
# Any other .py is a failure: the baseline lists no files and total 0.
git ls-files -- '*.py' ':!:third_party/**' ':!:**/.lake/**' \
  ':!:benchmarks/baselines/python/**' ':!:examples/interop/python/**' \
  | LC_ALL=C sort > "$OUT/current.txt"

if [[ "${1:-}" == "--update" ]]; then
  echo update > "$OUT/mode.txt"
else
  echo check > "$OUT/mode.txt"
fi

SRC=tools/python_ratchet/main.flow
BIN="$OUT/python_ratchet"
FLOWC="$OUT/flowc"
CC="${CC:-cc}"

if [[ ! -x "$FLOWC" || compiler/bootstrap/flowc_stage_a.c -nt "$FLOWC" ]]; then
  "$CC" -O1 -w -o "$FLOWC" compiler/bootstrap/flowc_stage_a.c -lm
fi
if [[ ! -x "$BIN" || "$SRC" -nt "$BIN" || "$FLOWC" -nt "$BIN" ]]; then
  FLOWC_TYPECHECK=1 FLOWC_IN="$SRC" FLOWC_OUT="$OUT/main.c" "$FLOWC"
  "$CC" -O2 -w -Iruntime -o "$BIN" "$OUT/main.c"
fi

exec "$BIN"
