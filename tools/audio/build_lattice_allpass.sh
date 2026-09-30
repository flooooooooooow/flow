#!/usr/bin/env bash
# Build scripts/tools/lattice_allpass and print the binary path.
#
# build_tool.sh only watches main.flow and scripts/tools/lib, so the cached
# binary is dropped first when any sibling module is newer than it.

set -euo pipefail

ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
cd "$ROOT"

BIN="build/flow-tools/lattice_allpass"
if [[ -x "$BIN" ]]; then
  for f in scripts/tools/lattice_allpass/*.flow lib/stdlib/audio/lattice_allpass.flow lib/stdlib/dynamics/schur_lattice.flow; do
    if [[ "$f" -nt "$BIN" ]]; then
      rm -f "$BIN"
      break
    fi
  done
fi
scripts/tools/build_tool.sh lattice_allpass
