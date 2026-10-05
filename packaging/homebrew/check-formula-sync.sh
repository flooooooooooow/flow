#!/usr/bin/env bash
set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
source_formula="$repo_root/packaging/homebrew/Formula/flow.rb"
tap_formula="${1:-${FLOW_HOMEBREW_TAP_FORMULA:-$repo_root/../homebrew-flow/Formula/flow.rb}}"

if [[ ! -f "$source_formula" ]]; then
  printf 'missing source formula: %s\n' "$source_formula" >&2
  exit 2
fi

if [[ ! -f "$tap_formula" ]]; then
  printf 'missing tap formula: %s\n' "$tap_formula" >&2
  printf 'pass the tap formula path explicitly, e.g. %s ../homebrew-flow/Formula/flow.rb\n' "$0" >&2
  exit 2
fi

if cmp -s "$source_formula" "$tap_formula"; then
  printf 'Homebrew formulas are synchronized.\n'
  exit 0
fi

printf 'Homebrew formulas differ:\n' >&2
diff -u "$source_formula" "$tap_formula" || true
exit 1
