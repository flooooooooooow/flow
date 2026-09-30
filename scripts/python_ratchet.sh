#!/usr/bin/env bash
# Fail when tracked Python grows. New code in this repository is written in Flow.
#
# The ratchet is the Flow program in tools/python_ratchet. It runs git
# itself through std.process; this script only builds it with the
# checked-in Stage-A bootstrap, so the check needs no Python.
#
# Usage:
#   ./scripts/python_ratchet.sh            check, exit 1 on new or grown Python
#   ./scripts/python_ratchet.sh --update   tighten the baseline after a port

set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

OUT=build/python-ratchet
mkdir -p "$OUT"

SRC=tools/python_ratchet/main.flow
BIN="$OUT/python_ratchet"
FLOWC="$OUT/flowc"
CC="${CC:-cc}"

if [[ ! -x "$FLOWC" || compiler/bootstrap/flowc_stage_a.c -nt "$FLOWC" ]]; then
  "$CC" -O1 -w -o "$FLOWC" compiler/bootstrap/flowc_stage_a.c -lm
fi
stale=0
for dep in "$SRC" "$FLOWC" lib/stdlib/process.flow lib/stdlib/bytebuf.flow compiler/src/bytebuf.flow; do
  if [[ ! -x "$BIN" || "$dep" -nt "$BIN" ]]; then
    stale=1
  fi
done
if [[ "$stale" -eq 1 ]]; then
  FLOWC_BUNDLE=1 FLOWC_DIR=. FLOWC_TYPECHECK=1 FLOWC_IN="$SRC" FLOWC_OUT="$OUT/main.c" "$FLOWC"
  "$CC" -O2 -w -o "$BIN" "$OUT/main.c"
fi

exec "$BIN" "$@"
