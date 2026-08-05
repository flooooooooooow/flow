#!/usr/bin/env bash
# Build & run the Schur all-pass DSP correctness tests (no JUCE needed).
set -euo pipefail
cd "$(dirname "$0")"
clang++ -O2 -std=c++17 dsp_test.cpp ../Source/SchurLatticeDSP.cpp -o dsp_test
./dsp_test
