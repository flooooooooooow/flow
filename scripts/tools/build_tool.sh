#!/usr/bin/env bash
# Build one Flow tool from scripts/tools/<name>/main.flow and print the path
# of the executable.
#
# Python-free: the Stage-A compiler is built from the checked-in bootstrap C
# with cc, then compiles the tool in bundle mode so it can import the shared
# helpers in scripts/tools/lib. Binaries are cached under build/flow-tools and
# rebuilt when the tool, the helpers or the bootstrap C change.
#
# Usage: scripts/tools/build_tool.sh <name>

set -euo pipefail

ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
cd "$ROOT"

NAME="${1:?usage: build_tool.sh <tool name>}"
SRC="scripts/tools/$NAME/main.flow"
LIB="scripts/tools/lib"
OUT_DIR="build/flow-tools"
FLOWC="$OUT_DIR/flowc"
BOOT_C="compiler/bootstrap/flowc_stage_a.c"
C_OUT="$OUT_DIR/$NAME.c"
BIN="$OUT_DIR/$NAME"
# flowc output silences int-conversion and pointer-type diagnostics for both
# clang and GCC (#958), so any C compiler works.
CC="${CC:-cc}"

if [[ ! -f "$SRC" ]]; then
  echo "build_tool: no such tool: $SRC" >&2
  exit 2
fi

mkdir -p "$OUT_DIR"

if [[ ! -x "$FLOWC" || "$BOOT_C" -nt "$FLOWC" ]]; then
  "$CC" -O1 -w -o "$FLOWC" "$BOOT_C" -lm
fi

stale=0
if [[ ! -x "$BIN" || "$FLOWC" -nt "$BIN" || "$SRC" -nt "$BIN" ]]; then
  stale=1
else
  for f in "$LIB"/*.flow; do
    if [[ "$f" -nt "$BIN" ]]; then
      stale=1
      break
    fi
  done
fi

if [[ "$stale" -eq 1 ]]; then
  if ! FLOWC_BUNDLE=1 FLOWC_DIR="$LIB" FLOWC_TYPECHECK=1 \
      FLOWC_IN="$SRC" FLOWC_OUT="$C_OUT" "$FLOWC" >"$OUT_DIR/$NAME.flowc.log" 2>&1; then
    cat "$OUT_DIR/$NAME.flowc.log" >&2
    echo "build_tool: flowc could not compile $SRC" >&2
    exit 1
  fi
  "$CC" -O2 -w -o "$BIN" "$C_OUT"
fi

printf '%s\n' "$BIN"
