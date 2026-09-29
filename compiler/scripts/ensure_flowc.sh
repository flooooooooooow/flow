#!/usr/bin/env bash
# Ensure a Stage-A flowc driver binary exists under compiler/build.
#
# Order:
#   1. an already-built self-hosted driver that is newer than compiler/src;
#   2. compiler/build/flowc_bootstrap, built with cc from the checked-in
#      bootstrap C, unless compiler/src has local edits the checked-in C
#      cannot reflect;
#   3. for those local edits, a flowc that the bootstrap binary compiles from
#      the current compiler/src (compiler/scripts/flowc_host.sh).
# No step needs Python.
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

compiler_sources_newer_than() {
    local target="$1"
    [[ -e "$target" ]] || return 0
    find compiler/src -type f -newer "$target" -print -quit | grep -q .
}

# True when compiler/src differs from what the checked-in bootstrap C was
# generated from.
compiler_sources_edited() {
    if command -v git >/dev/null 2>&1 && \
            git rev-parse --is-inside-work-tree >/dev/null 2>&1; then
        [[ -n "$(git status --porcelain -- compiler/src 2>/dev/null)" ]]
        return
    fi
    # Not a git checkout (release tarball, copied tree): fall back to mtimes.
    compiler_sources_newer_than "$BOOT_C"
}

pick_selfhosted() {
    local cand
    for cand in \
        compiler/build/stage_a_driver_flow_self \
        compiler/build/stage_a_driver_flow_g2 \
        compiler/build/stage_a_driver_flow \
        compiler/build/stage_a_driver_g2 \
        compiler/build/stage_a_driver
    do
        if [[ -x "$cand" ]] && ! compiler_sources_newer_than "$cand"; then
            printf '%s\n' "$cand"
            return 0
        fi
    done
    return 1
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

# --cc-only: the driver built from the checked-in bootstrap C and nothing
# else. flow-driver builds its helper tools (pkg_sync, the package manager)
# with it, and flowc_host.sh starts from it.
if [[ "${1:-}" == "--cc-only" ]]; then
    if [[ -f "$BOOT_C" ]] && build_bootstrap; then
        printf '%s\n' "$BOOT_BIN"
        exit 0
    fi
    echo "ensure_flowc: bootstrap C did not build" >&2
    exit 1
fi

if pick_selfhosted >/dev/null; then
    pick_selfhosted
    exit 0
fi

if [[ ! -f "$BOOT_C" ]]; then
    echo "ensure_flowc: no flowc driver available (need cc and $BOOT_C)" >&2
    exit 1
fi

if compiler_sources_edited; then
    # A flowc compiled from the current compiler/src by the bootstrap binary.
    echo "ensure_flowc: compiler/src has local edits; building flowc from them" >&2
    exec bash compiler/scripts/flowc_host.sh
fi

if build_bootstrap; then
    printf '%s\n' "$BOOT_BIN"
    exit 0
fi
echo "ensure_flowc: bootstrap C did not build" >&2
exit 1
