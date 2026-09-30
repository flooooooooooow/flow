#!/usr/bin/env bash
# Real audio through the modulating Schur-lattice all-pass.
#
# Writes build/audio/lattice_allpass/{input,output_static_allpass,
# output_modulated_allpass}.wav (16-bit mono, 48 kHz, 3 s) and seven SVG
# figures under build/plots/schur_lattice_allpass/, copied to
# docs/research/schur_lattice_allpass/figures/.
#
# The program is the Flow tool scripts/tools/lattice_allpass (mode `demo`).
#
# Usage: tools/audio/lattice_allpass_audio_demo.sh [--no-open]

set -euo pipefail

ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
cd "$ROOT"

BIN="$(tools/audio/build_lattice_allpass.sh)"
exec "$BIN" demo "$@"
