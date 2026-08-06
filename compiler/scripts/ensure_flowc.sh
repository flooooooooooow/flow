#!/usr/bin/env bash
# Ensure a Stage-A flowc driver binary exists under compiler/build/.
# Order: an already-built self-hosted driver, then the checked-in bootstrap C
# (cc only, no Python), then the Python Gen0 roundtrip as a last resort.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
cd "$ROOT"
mkdir -p compiler/build

pick_flowc() {
    local cand
    for cand in \
        compiler/build/stage_a_driver_flow_self \
        compiler/build/stage_a_driver_flow_g2 \
        compiler/build/stage_a_driver_flow \
        compiler/build/stage_a_driver_g2 \
        compiler/build/stage_a_driver \
        compiler/build/flowc_bootstrap
    do
        if [[ -x "$cand" ]]; then
            printf '%s\n' "$cand"
            return 0
        fi
    done
    return 1
}

if pick_flowc >/dev/null; then
    pick_flowc
    exit 0
fi

# Python-free path: compile the checked-in bootstrap translation unit.
# compiler/bootstrap/flowc_stage_a.c is driver.flow plus its imports, emitted
# by flowc itself, so this needs a C compiler and nothing else.
if [[ -f compiler/bootstrap/flowc_stage_a.c ]]; then
    echo "ensure_flowc: building flowc_bootstrap from checked-in C (cc only)..." >&2
    if "${CC:-cc}" ${CFLAGS:--O2} -o compiler/build/flowc_bootstrap \
            compiler/bootstrap/flowc_stage_a.c 2>/dev/null; then
        printf '%s\n' compiler/build/flowc_bootstrap
        exit 0
    fi
    echo "ensure_flowc: bootstrap C did not build — falling back to the Python host" >&2
fi

echo "ensure_flowc: no driver yet — bootstrapping Gen0 (Python host)..." >&2
chmod +x ./flow compiler/scripts/*.sh
# Bootstrap must use the Python host (Gen0); avoid recurse via FLOW_HOST=flowc.
FLOW_HOST=python ./compiler/scripts/roundtrip.sh >/dev/null

if ! pick_flowc >/dev/null; then
    echo "ensure_flowc: bootstrap finished but no stage_a_driver* binary found" >&2
    exit 1
fi
pick_flowc
