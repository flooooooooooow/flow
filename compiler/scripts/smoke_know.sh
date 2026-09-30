#!/usr/bin/env bash
# Smoke: compile (flowc) know_demo and check fingerprint / know string constants.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
cd "$ROOT"
OUT="${1:-compiler/build/know_demo.c}"
mkdir -p "$(dirname "$OUT")"
compiler/scripts/flowc_emit.sh --lenient \
  examples/compilers/know_demo.flow "$OUT"

need=(
  'know+fingerprint: PASS'
  '0+n=n'
  'Nat/addition#0+n=n'
  'Bool.disjunction.order_does_not_matter'
  'coordinate:'
)
for s in "${need[@]}"; do
  if ! grep -Fq "$s" "$OUT"; then
    echo "FAIL: missing in $OUT: $s"
    exit 1
  fi
done
echo "PASS know/fingerprint C smoke ($OUT)"
exit 0
