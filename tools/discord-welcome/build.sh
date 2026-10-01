#!/usr/bin/env bash
# Build the Flow welcome bot (scripts/tools/discord_welcome) and print the
# path of the executable.
#
# Same pipeline as `./flow tool` (Stage-A flowc from the
# checked-in bootstrap C, bundle mode), plus OpenSSL at link time: Homebrew
# openssl@3 on macOS, pkg-config or plain -lssl -lcrypto elsewhere.
#
# Usage: tools/discord-welcome/build.sh [OUTPUT]

set -euo pipefail

ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
cd "$ROOT"

NAME="discord_welcome"
SRC_DIR="scripts/tools/$NAME"
LIB="scripts/tools/lib"
OUT_DIR="build/flow-tools"
FLOWC="$OUT_DIR/flowc"
BOOT_C="compiler/bootstrap/flowc_stage_a.c"
C_OUT="$OUT_DIR/$NAME.c"
BIN="${1:-$OUT_DIR/$NAME}"
CC="${CC:-cc}"

mkdir -p "$OUT_DIR"
if [[ ! -x "$FLOWC" || "$BOOT_C" -nt "$FLOWC" ]]; then
  "$CC" -O1 -w -o "$FLOWC" "$BOOT_C" -lm
fi

stale=0
if [[ ! -x "$BIN" || "$FLOWC" -nt "$BIN" ]]; then
  stale=1
else
  for f in "$SRC_DIR"/*.flow "$LIB"/*.flow; do
    if [[ "$f" -nt "$BIN" ]]; then
      stale=1
      break
    fi
  done
fi

if [[ "$stale" -eq 1 ]]; then
  ssl_cflags=()
  ssl_libs=(-lssl -lcrypto)
  prefix=""
  if command -v brew >/dev/null 2>&1; then
    prefix="$(brew --prefix openssl@3 2>/dev/null || true)"
  fi
  if [[ -n "$prefix" && -d "$prefix/lib" ]]; then
    ssl_libs=(-L"$prefix/lib" -Wl,-rpath,"$prefix/lib" -lssl -lcrypto)
  elif pkg-config --exists openssl 2>/dev/null; then
    # shellcheck disable=SC2207
    ssl_libs=($(pkg-config --libs openssl))
  fi
  if ! FLOWC_BUNDLE=1 FLOWC_DIR="$LIB" FLOWC_TYPECHECK=1 \
      FLOWC_IN="$SRC_DIR/main.flow" FLOWC_OUT="$C_OUT" "$FLOWC" >"$OUT_DIR/$NAME.flowc.log" 2>&1; then
    cat "$OUT_DIR/$NAME.flowc.log" >&2
    echo "discord-welcome build: flowc could not compile $SRC_DIR/main.flow" >&2
    exit 1
  fi
  mkdir -p "$(dirname "$BIN")"
  "$CC" -O2 -w ${ssl_cflags[@]+"${ssl_cflags[@]}"} -o "$BIN" "$C_OUT" "${ssl_libs[@]}"
fi

printf '%s\n' "$BIN"
