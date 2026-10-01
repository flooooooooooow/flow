#!/usr/bin/env bash
# Ensure a flowc binary exists under compiler/build and print its path.
#
#   1. compiler/build/flowc_bootstrap, built with cc from the checked-in
#      bootstrap C, unless compiler/src has local edits the checked-in C
#      cannot reflect;
#   2. for those local edits, a flowc that the bootstrap binary compiles from
#      the current compiler/src (compiler/scripts/flowc_host.sh).
# Both are complete main.flow builds of flowc. No step needs Python.
#
# The Stage-A driver.flow binaries that roundtrip.sh leaves in compiler/build
# (stage_a_driver_flow and friends) are test artifacts with a smaller feature
# set, so they are never picked here. FLOWC_BIN selects any binary explicitly.
#
# "Local edits" means uncommitted changes under compiler/src when this is a git
# work tree. File modification times are not used for that decision: a fresh
# clone writes compiler/src after compiler/bootstrap, so by mtime the sources
# always look newer than the bootstrap C.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
cd "$ROOT"
mkdir -p compiler/build

BOOT_C=compiler/bootstrap/flowc_stage_a.c
BOOT_BIN=compiler/build/flowc_bootstrap

# True when compiler/src differs from what the checked-in bootstrap C was
# generated from.
compiler_sources_edited() {
    if command -v git >/dev/null 2>&1 && \
            git rev-parse --is-inside-work-tree >/dev/null 2>&1; then
        [[ -n "$(git status --porcelain -- compiler/src 2>/dev/null)" ]]
        return
    fi
    # Not a git checkout (release tarball, copied tree): fall back to mtimes.
    find compiler/src -type f -newer "$BOOT_C" -print -quit | grep -q .
}

# Build compiler/build/flowc_bootstrap from the checked-in C with cc alone.
# Writes to a temporary name first so concurrent runs never see a partial
# binary.
build_bootstrap() {
    if [[ -x "$BOOT_BIN" && ! "$BOOT_C" -nt "$BOOT_BIN" ]]; then
        return 0
    fi
    echo "ensure_flowc: building flowc_bootstrap from checked-in C (cc only)..." >&2
    local tmp="$BOOT_BIN.tmp.$$"
    # shellcheck disable=SC2086
    if "${CC:-cc}" ${CFLAGS:--O2} -o "$tmp" "$BOOT_C" -lm 2>/dev/null; then
        mv -f "$tmp" "$BOOT_BIN"
        return 0
    fi
    rm -f "$tmp"
    return 1
}

if [[ ! -f "$BOOT_C" ]]; then
    echo "ensure_flowc: no flowc driver available (need cc and $BOOT_C)" >&2
    exit 1
fi

# --cc-only: the binary built from the checked-in bootstrap C and nothing
# else. The flow CLI builds its helper tools (pkg_sync, the package manager)
# with it, and flowc_host.sh starts from it.
if [[ "${1:-}" != "--cc-only" ]] && compiler_sources_edited; then
    echo "ensure_flowc: compiler/src has local edits; building flowc from them" >&2
    exec bash compiler/scripts/flowc_host.sh
fi

if build_bootstrap; then
    printf '%s\n' "$BOOT_BIN"
    exit 0
fi
echo "ensure_flowc: bootstrap C did not build" >&2
exit 1
