#!/usr/bin/env bash
# Benchmarks for docs/library/tiny-pointers.md §Benchmarks.
#
# The tiny-pointers demo is parameterized by n: every table geometry, load
# and op count is a constant proportional to n. This script re-derives the
# constants at a few sizes (n = 2^14 .. 2^17), compiles each variant to a
# native binary with the Python host (-O2), runs it (best of 3, exit 0 = PASS),
# and prints the per-phase wall-clock times the binary reports itself.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
SRC="$ROOT/examples/systems/tiny_pointers.flow"
WORK="${TMPDIR:-/tmp}/flow-tp-bench"
mkdir -p "$WORK"

sizes=(16384 32768 65536)

# Re-derive the n-proportional constants of the demo at a given size.
scale_src() { # $1 = out file, $2 = n
    python3 - "$SRC" "$2" > "$1" <<'PY'
import math, sys
src = open(sys.argv[1]).read()
n = int(sys.argv[2])
f = n / 65536.0
subs = {
    "const N_SLOTS: i32 = 65536": n,
    "const LOG_N: i32 = 16": int(math.log2(n)),
    "const MAX_LIVE: i32 = 49152": int(49152 * f),
    "const P_SLOTS: i32 = 57344": int(57344 * f),
    "const P_BUCKETS: i32 = 1792": int(1792 * f),
    "const S_SLOTS: i32 = 8192": int(8192 * f),
    "const S_BUCKETS: i32 = 1024": int(1024 * f),
    "const REG_SIZE: i32 = 131072": int(131072 * f),
    "const V_MAX_LIVE: i32 = 49152": int(49152 * f),
    "const R_MAX_LIVE: i32 = 49152": int(49152 * f),
    "const RH_CAP: i32 = 131072": int(131072 * f),
    "const CHURN_OPS: i32 = 30000": int(30000 * f),
    "const R_CHURN_OPS: i32 = 20000": int(20000 * f),
    "const RR_N: i32 = 16384": int(16384 * f),
    "const RR_CHURN: i32 = 8000": int(8000 * f),
    "const BST_N: i32 = 16384": int(16384 * f),
    "const BST_STORM: i32 = 20000": int(20000 * f),
    "const VD_MAX_KEYS: i32 = 49152": int(49152 * f),
    "const KD_MAX_KEYS: i32 = 49152": int(49152 * f),
    "const RV_LOAD: i32 = 30000": int(30000 * f),
    "const RV_CHURN: i32 = 20000": int(20000 * f),
    "const RV_DRAIN: i32 = 26000": int(26000 * f),
    "const RV_RELOAD: i32 = 25000": int(25000 * f),
    "const RL_KEYS: i32 = 12288": int(12288 * f),
    "const RL_CHURN: i32 = 4000": int(4000 * f),
    "const RL_ARENA_B: i32 = 2048": int(2048 * f),
    "const RL3_KEYS: i32 = 12288": int(12288 * f),
    "const RL3_CHURN: i32 = 3000": int(3000 * f),
    "const RL3_ARENA_B: i32 = 512": int(512 * f),
    "const RL3_P2_B: i32 = 512": int(512 * f),
    "const RL3_POOL_WORDS: i32 = 524288": int(524288 * f),
    "const ST_M: i32 = 8192": int(8192 * f),
    "const ST_NB: i32 = 4096": int(4096 * f),
    "const ST_B: i32 = 8": 8,
    "const ST_EXT: i32 = 32768": int(32768 * f),
    "const ST_BINS: i32 = 2048": int(2048 * f),
    "const ST_Q_BITS: i32 = 11": int(math.log2(2048 * f)),
    "const ST_CHURN: i32 = 6000": int(6000 * f),
    "const ST_QUERIES: i32 = 16384": int(16384 * f),
}
for k, v in subs.items():
    assert k in src, "missing const line: " + k
    src = src.replace(k, k.split("= ")[0] + "= " + str(v))
sys.stdout.write(src)
PY
}

phases=(
    "1 bulk load" "2 dynamic churn" "3 stability churn" "4 stable dict"
    "5 natural load" "6 adversarial + tail" "7 retrieval load"
    "8 churn + rebuild" "9 AVL build" "10 rotation storm"
    "11 variable-value dict" "12 variable-key+value"
    "13 lower bounds" "14 deamortized resize" "15 r-levels chain"
    "16 optimal stash" "8b r-tradeoff"
)

log2i() { # $1 = n -> log2(n) on stdout
    local v=$1 lg=0
    while (( v > 1 )); do
        (( v >>= 1, lg++ ))
    done
    echo "$lg"
}

for size in "${sizes[@]}"; do
    variant="$WORK/tiny_pointers_$size.flow"
    scale_src "$variant" "$size"
    FLOW_HOST=python FLOW_CFLAGS='-O2' "$ROOT/flow" compile "$variant" >/dev/null 2>&1
    bin="$ROOT/build/tiny_pointers_$size"
    for r in 1 2 3; do
        out="$WORK/out_${size}_${r}.txt"
        "$bin" > "$out" 2>&1 || { echo "size $size run $r: binary failed"; exit 1; }
        grep -q 'PASS —' "$out" || { echo "size $size run $r: no PASS"; exit 1; }
    done
    # best-of-3 per phase, from the binary's own CLOCK_MONOTONIC report
    for r in 1 2 3; do
        sed -nE 's/^  Phase ([0-9]+[a-z]*) .*: +([0-9.]+) ms$/\1 \2/p' \
            "$WORK/out_${size}_${r}.txt"
    done | awk '{ k = ($1 == "8b" ? 17 : $1 + 0); if (!(k in m) || $2 + 0 < m[k]) m[k] = $2 + 0 }
                END { for (p = 1; p <= 17; p++) printf "%d %.2f\n", p, m[p] }' \
        > "$WORK/best_$size.txt"
done

echo "tiny-pointers wall-clock (CLOCK_MONOTONIC, native -O2 binary, best of 3 runs)"
echo "  machine: $(uname -sm) $(sw_vers -productVersion 2>/dev/null || true)"
echo "  compiler: $(clang --version | head -1)"
printf "%-22s" "phase"
for size in "${sizes[@]}"; do
    printf " %9s" "n=2^$(log2i "$size")"
done
echo
for p in 1 2 3 4 5 6 7 8 9 10 11 12 13 14 15 16 17; do
    printf "%-22s" "${phases[$((p - 1))]}"
    for size in "${sizes[@]}"; do
        awk -v p="$p" '$1 == p {print $2}' "$WORK/best_$size.txt"
    done | xargs printf " %9s"
    echo
done
printf "%-22s" "total"
for size in "${sizes[@]}"; do
    awk '{s += $2} END {printf "%.2f\n", s}' "$WORK/best_$size.txt"
done | xargs printf " %9s"
echo

# The paper's abstract promises two pointer results and five applications;
# this map links each to the bench row(s) that measure it and to its doc
# section — the same table as the 'Abstract-claim coverage' sections of
# docs/library/tiny-pointers.md and tiny-pointers-variable-values.md, and as
# the map the demo prints at the top of its own run output.
print_coverage_map() {
    echo
    echo "Abstract-claim coverage  (arXiv:2111.12800 → phase · doc section)"
    echo "──────────────────────────────────────────────────────────────────"
    echo "  pointer results:"
    echo "    · fixed-size Θ(log log log n + log k) bits   → Theorem 1 (Phases 1–4)"
    echo "    · variable-size Θ(log k) expected bits       → Theorem 2 (Phases 5–6)"
    echo "  applications:"
    echo "    ① relaxed retrieval nv + O(n log⁽ʳ⁾ n), O(1)-expected hints, O(r) insert/delete"
    echo "        → Theorem 6 (Phases 7–8, 8b)  ·  §6.2"
    echo "    ② succinct rotation-based BSTs               → Theorem 7 (Phases 9–10)  ·  §6.3"
    echo "    ③ stable fixed-capacity dicts, 1 + o(1)      → Theorem 8 (Phases 3–4)  ·  §6.4"
    echo "    ④ arbitrary-size values, log⁽ʳ⁾ n + O(log j) → Theorem 9 (Phases 11/12/14/15)  ·  §6.5"
    echo "        (deep dive: docs/library/tiny-pointers-variable-values.md)"
    echo "    ⑤ optimal internal-memory stash O(n log ε⁻¹) → Theorem 10 (Phase 16)  ·  §6.6"
    echo "  (Theorems 3–5 are lower bounds / intermediate steps, not constructions.)"
    echo "  full theorem table: docs/library/tiny-pointers.md"
    echo "──────────────────────────────────────────────────────────────────"
    echo
}

print_coverage_map
