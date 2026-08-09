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

# TeX-ish needles contain literal backslashes (the demo asserts strings with
# escaped backslashes, so the emitted C text carries two backslash bytes).
need=(
  'zero is the left identity, for addition on the natural numbers'
  '0 + n == n'
  'm + n == n + m'
  'math_prose+proof_sub: PASS'
  'We stipulate zero is the left identity for addition on the natural numbers'
  'x holds'
  'x does not hold'
  'count is zero'
  'x  equals  y'
  'the conjunction of the disjunction of a and b and c'
  'the disjunction of the disjunction of x and y and z'
  'the successor of n equals n plus 1'
  'm times n equals 0'
  $'m \\\\cdot n = 0'
  $'\\\\alpha\' = 180^\\\\circ'
  'S_{5}(x)'
  $'\\\\sin\'(0) = \\\\quad (x \\\\to 0)'
  $'x \\\\ge 0 \\\\land x \\\\le 10'
  $'\\\\text{x y} = \\\\text{z 2}'
  'x y equals z 2'
)
for s in "${need[@]}"; do
  if ! grep -Fq "$s" "$OUT"; then
    echo "FAIL: missing in $OUT: $s"
    exit 1
  fi
done
echo "PASS math_prose/proof_sub C smoke ($OUT)"
exit 0
