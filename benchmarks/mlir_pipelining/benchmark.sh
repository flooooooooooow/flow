#!/usr/bin/env bash
# Software pipelining and multi-buffering: optimize a memory-bound MLIR loop
# at O3 with and without --enable-loop-pipelining --enable-multi-buffering
# (compiler/scripts/mlir_optimize.sh; loop fusion on, as the retired
# mlir_optimizer.py command line had it), lower, build, and time five runs
# three times. Writes benchmarks/mlir_pipelining/benchmark_report.txt.
set -uo pipefail
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd -P)"
ROOT="$(cd "$HERE/../.." && pwd -P)"

work="$(mktemp -d "${TMPDIR:-/tmp}/flow-pipelining.XXXXXX")"
trap 'rm -rf "$work"' EXIT

cat > "$work/in.mlir" <<'EOF'
module {
  func.func @main() -> i32 {
    %c0 = arith.constant 0 : index
    %c10000000 = arith.constant 10000000 : index
    %c1 = arith.constant 1 : index

    %c0_i32 = arith.constant 0 : i32
    %c1_i32 = arith.constant 1 : i32
    %c2_i32 = arith.constant 2 : i32
    %c3_i32 = arith.constant 3 : i32

    %alloc_a = memref.alloc() : memref<10000000xi32>
    %alloc_b = memref.alloc() : memref<10000000xi32>
    %alloc_c = memref.alloc() : memref<10000000xi32>

    scf.for %iv = %c0 to %c10000000 step %c1 {
       memref.store %c1_i32, %alloc_a[%iv] : memref<10000000xi32>
       memref.store %c2_i32, %alloc_b[%iv] : memref<10000000xi32>
    }

    scf.for %iv = %c0 to %c10000000 step %c1 {
      %v1 = memref.load %alloc_a[%iv] : memref<10000000xi32>
      %v2 = memref.load %alloc_b[%iv] : memref<10000000xi32>
      %v3 = arith.muli %v1, %c2_i32 : i32
      %v4 = arith.addi %v3, %v2 : i32
      %v5 = arith.muli %v4, %c3_i32 : i32
      memref.store %v5, %alloc_c[%iv] : memref<10000000xi32>
    }

    %res = memref.load %alloc_c[%c0] : memref<10000000xi32>
    return %res : i32
  }
}
EOF

now_ms() {
    perl -MTime::HiRes=time -e 'printf "%.3f\n", time * 1000'
}

# run TAG FLAGS...: prints "RESULT MS" (exit status, best per-run time).
run() {
    local tag="$1"
    shift
    "$ROOT/compiler/scripts/mlir_optimize.sh" --opt-level O3 --loop-fusion "$@" \
        "$work/in.mlir" "$work/$tag.mlir" || return 1
    "$ROOT/compiler/scripts/mlir_lower.sh" "$work/$tag.mlir" "$work/$tag.ll" || return 1
    clang -O2 -Wno-override-module "$work/$tag.ll" -o "$work/$tag" -lm || return 1
    local best="" res=0 k j t0 t1 dt
    for k in 1 2 3; do
        t0="$(now_ms)"
        for j in 1 2 3 4 5; do
            res=0
            "$work/$tag" || res=$?
        done
        t1="$(now_ms)"
        dt="$(awk -v a="$t0" -v b="$t1" 'BEGIN { printf "%.3f", (b - a) / 5 }')"
        if [[ -z "$best" ]] || awk -v a="$dt" -v b="$best" 'BEGIN { exit !(a < b) }'; then
            best="$dt"
        fi
    done
    echo "$res $best"
}

echo "Running without pipelining..."
read -r res_base time_base < <(run base) || exit 1
printf 'Result: %s, Time: %.2f ms\n' "$res_base" "$time_base"

echo ""
echo "Running with pipelining..."
read -r res_pipe time_pipe < <(run pipe --enable-loop-pipelining --enable-multi-buffering) || exit 1
printf 'Result: %s, Time: %.2f ms\n' "$res_pipe" "$time_pipe"

diff="$(awk -v a="$time_base" -v b="$time_pipe" 'BEGIN { printf "%.2f", a - b }')"
pct="$(awk -v a="$time_base" -v b="$time_pipe" 'BEGIN { printf "%.2f", (a - b) / a * 100 }')"
echo ""
echo "Speedup: ${pct}% (${diff} ms)"

reasoning=""
if awk -v p="$pct" 'BEGIN { exit !(p < 5.0) }'; then
    reasoning=" (Note: software pipelining and multi-buffering gain little here. Out-of-order CPUs already overlap the memory latency this loop exposes. MLIR's scf pipelining transform mostly targets statically scheduled hardware: spatial architectures, VLIW and DSPs.)"
fi
{
    echo "MLIR Pipelining Benchmark"
    printf 'Baseline: %.2f ms\n' "$time_base"
    printf 'Pipelined: %.2f ms\n' "$time_pipe"
    echo "Speedup: ${pct}%${reasoning}"
} > "$HERE/benchmark_report.txt"
