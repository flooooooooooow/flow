#!/usr/bin/env bash
# Print the path of a flowc built from the current compiler/src.
#
# This is the compiler host for work on flowc itself. The checked-in bootstrap
# C (compiler/bootstrap/flowc_stage_a.c) is built with cc, and that binary
# compiles compiler/src/main.flow in bundle mode. The result is a complete
# flowc (self-tests with no FLOWC_IN, C emit with FLOWC_IN/FLOWC_OUT) that
# reflects any local edits under compiler/src. No Python is involved.
#
#   host="$(compiler/scripts/flowc_host.sh)"
#   FLOWC_IN=prog.flow FLOWC_OUT=prog.c "$host"
#
# The binary is cached under compiler/build/flowc_host/<key>/flowc, keyed on
# the contents of compiler/src and the bootstrap C, so repeated calls cost a
# checksum. Builds go to a temporary name first so concurrent callers never
# see a half-written binary.
#
# Env:
#   FLOWC_HOST_BIN=<path>  use this binary instead (printed as is)
#   CC                     C compiler (default cc)
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
cd "$ROOT"

if [[ -n "${FLOWC_HOST_BIN:-}" ]]; then
    printf '%s\n' "$FLOWC_HOST_BIN"
    exit 0
fi

BOOT_C=compiler/bootstrap/flowc_stage_a.c
CC="${CC:-cc}"

key="$(cat "$BOOT_C" compiler/src/*.flow | cksum | awk '{print $1 "-" $2}')"
dir="compiler/build/flowc_host/$key"
bin="$dir/flowc"
if [[ -x "$bin" ]]; then
    printf '%s\n' "$ROOT/$bin"
    exit 0
fi

boot="$(bash compiler/scripts/ensure_flowc.sh --cc-only)"
[[ "$boot" == /* ]] || boot="$ROOT/$boot"

mkdir -p "$dir"
tmp="$dir/flowc.tmp.$$"
if ! FLOWC_BUNDLE=1 FLOWC_DIR=compiler/src FLOWC_IN=compiler/src/main.flow \
        FLOWC_OUT="$tmp.c" "$boot" >"$tmp.log" 2>&1; then
    echo "flowc_host: $boot could not compile compiler/src/main.flow" >&2
    cat "$tmp.log" >&2
    rm -f "$tmp.c" "$tmp.log"
    exit 1
fi
if ! "$CC" -O2 -w -o "$tmp" "$tmp.c" -lm; then
    echo "flowc_host: $CC could not build the emitted compiler" >&2
    rm -f "$tmp" "$tmp.c" "$tmp.log"
    exit 1
fi
rm -f "$tmp.c" "$tmp.log"
mv -f "$tmp" "$bin"
printf '%s\n' "$ROOT/$bin"
