#!/usr/bin/env bash
# Smoke: transpile math_prose + proof_sub demo and check expected string constants
# in the generated C (host may hang on newly linked Mach-Os).
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
cd "$ROOT"
OUT="${1:-compiler/build/math_prose_demo.c}"
mkdir -p "$(dirname "$OUT")"
PYTHONPATH=src python3 -m flow.transpiler \
  examples/compilers/math_prose_demo.flow --c --lenient -o "$OUT"

need=(
  'zero is the left identity, for addition on the natural numbers'
  '0 + n == n'
  'm + n == n + m'
  'math_prose+proof_sub: PASS'
  'We stipulate zero is the left identity for addition on the natural numbers'
)
for s in "${need[@]}"; do
  if ! grep -Fq "$s" "$OUT"; then
    echo "FAIL: missing in $OUT: $s"
    exit 1
  fi
done
echo "PASS math_prose/proof_sub C smoke ($OUT)"
exit 0
