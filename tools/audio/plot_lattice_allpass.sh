#!/usr/bin/env bash
# Schur-lattice all-pass verification and publication figures.
#
# Builds the Lean proofs (formal/SchurLatticeAllpass, lake build), runs
# lib/verify/SchurLattice.flow and examples/audio/lattice_allpass_demo.flow,
# draws schur_lattice_novel_demo.svg and schur_lattice_allpass_overview.svg,
# then runs the audio demo. Exits 1 unless the proofs, the verifier and the
# demo all pass.
#
# The program is the Flow tool scripts/tools/lattice_allpass (mode `plot`).
#
# Usage: tools/audio/plot_lattice_allpass.sh [--no-open] [--skip-lean]

set -euo pipefail

ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
cd "$ROOT"

BIN="$(tools/audio/build_lattice_allpass.sh)"
exec "$BIN" plot "$@"
