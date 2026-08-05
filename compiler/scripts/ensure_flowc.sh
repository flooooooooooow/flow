#!/usr/bin/env bash
# Ensure a Stage-A flowc driver binary exists under compiler/build/.
# Prefers self-hosted drivers; bootstraps Gen0 via Phase-A roundtrip if needed
# (Gen0 bootstrap still uses the Python host once).
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
        compiler/build/stage_a_driver
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

echo "ensure_flowc: no driver yet — bootstrapping Gen0 (Phase-A roundtrip)..." >&2
chmod +x ./flow compiler/scripts/*.sh
FLOWC_PHASE_A_ONLY=1 ./compiler/scripts/roundtrip.sh >/dev/null

if ! pick_flowc >/dev/null; then
    echo "ensure_flowc: bootstrap finished but no stage_a_driver* binary found" >&2
    exit 1
fi
pick_flowc
