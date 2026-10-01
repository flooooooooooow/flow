#!/usr/bin/env bash
# Build and run every published benchmark once, in hand-written C and in Flow,
# with the flags benchmarks/run_publish.sh uses, and check that the two agree.
#
# The programs time themselves with a monotonic clock. The helper that reads
# it must build on Linux and macOS alike (#964), so implicit function
# declarations are errors here even where the compiler would only warn.
#
#   ./scripts/check_bench_publish.sh

set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd -P)"
PUB="$ROOT/benchmarks/publish"
CC_BIN="${CC:-cc}"
if command -v clang >/dev/null 2>&1; then
    CC_BIN=clang
fi

work="$(mktemp -d "${TMPDIR:-/tmp}/flow-bench-publish.XXXXXX")"
trap 'rm -rf "$work"' EXIT

fail=0
for name in fib nbody matmul spectral mandelbrot; do
    if ! "$CC_BIN" -O2 -Werror=implicit-function-declaration \
            "$PUB/c/$name.c" -o "$work/${name}_c" -lm 2> "$work/${name}_c.err"; then
        echo "FAIL $name: hand-written C does not build"
        sed 's/^/     /' "$work/${name}_c.err" | head -n 10
        fail=$((fail + 1))
        continue
    fi
    if ! "$ROOT/flow" tool "$ROOT/compiler/scripts/flowc_emit.flow" --lenient "$PUB/flow/$name.flow" \
            "$work/${name}_flow.c" > "$work/${name}_emit.log" 2>&1; then
        echo "FAIL $name: flowc could not emit the Flow program"
        sed 's/^/     /' "$work/${name}_emit.log" | tail -n 10
        fail=$((fail + 1))
        continue
    fi
    if ! "$CC_BIN" -O2 -Werror=implicit-function-declaration \
            "$work/${name}_flow.c" -o "$work/${name}_flow" -lm 2> "$work/${name}_flow.err"; then
        echo "FAIL $name: Flow-generated C does not build"
        sed 's/^/     /' "$work/${name}_flow.err" | head -n 10
        fail=$((fail + 1))
        continue
    fi
    c_out="$("$work/${name}_c")"
    flow_out="$("$work/${name}_flow")"
    c_res="$(grep '^result ' <<< "$c_out" || true)"
    flow_res="$(grep '^result ' <<< "$flow_out" || true)"
    if [[ -z "$c_res" ]] || ! grep -q '^seconds ' <<< "$c_out" \
            || ! grep -q '^seconds ' <<< "$flow_out"; then
        echo "FAIL $name: missing result or seconds line"
        fail=$((fail + 1))
        continue
    fi
    if [[ "$c_res" != "$flow_res" ]]; then
        echo "FAIL $name: C says '$c_res', Flow says '$flow_res'"
        fail=$((fail + 1))
        continue
    fi
    echo "PASS $name ($c_res)"
done

if [[ "$fail" -ne 0 ]]; then
    echo "check_bench_publish: $fail failed"
    exit 1
fi
echo "check_bench_publish: PASS"
