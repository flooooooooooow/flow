#!/usr/bin/env bash
# Build a Flow program through MLIR and call one of its functions.
#
#   scripts/run_bench.sh PROGRAM.flow [FUNCTION]
#
# FUNCTION defaults to run_demo for a path with "demo" or "test" in it,
# run_bench for one with "main", else main. The program is emitted with the
# Flow MLIR emitter (`flow flow-to-mlir`), lowered with
# `flow mlir-lower`, and linked at -O3 -march=native with a small C runner that
# calls FUNCTION and supplies the JIT runtime helpers (jit_print, jit_time,
# jit_reload_check). This replaces scripts/run_bench.py, which loaded the
# same code as a shared object through ctypes.
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd -P)"

input="${1:?usage: run_bench.sh PROGRAM.flow [FUNCTION]}"
func="${2:-}"
if [[ -z "$func" ]]; then
    case "$input" in
        *demo*|*test*) func=run_demo ;;
        *main*) func=run_bench ;;
        *) func=main ;;
    esac
fi
echo "Reading $input..."

work="$(mktemp -d "${TMPDIR:-/tmp}/flow-bench.XXXXXX")"
trap 'rm -rf "$work"' EXIT

"$ROOT/flow" flow-to-mlir "$input" "$work/bench.mlir"
echo "Lowering MLIR to LLVM..."
"$ROOT/flow" mlir-lower "$work/bench.mlir" "$work/bench.ll"

cat > "$work/runner.c" <<EOF
#include <stdio.h>
#include <time.h>

/* Runtime helpers for Flow JIT programs. */
void jit_print(const char *message) { printf("%s\\n", message); }
double jit_time(void) { return (double)clock() / CLOCKS_PER_SEC; }
int jit_reload_check(void) { return 1; }

extern int $func(void);

int main(void) {
    return $func();
}
EOF
if [[ "$func" == main ]]; then
    # The program's own main is the entry point.
    sed -i.bak -e '/^extern int main(void);/d' -e '/^int main(void) {/,/^}/d' "$work/runner.c"
fi

echo "Compiling benchmark..."
march=(-march=native)
clang "${march[@]}" -O3 -Wno-override-module "$work/bench.ll" "$work/runner.c" \
    -o "$work/bench" -lm
echo "🚀 Running $func..."
echo "----------------------------------------"
rc=0
"$work/bench" || rc=$?
echo "----------------------------------------"
exit "$rc"
