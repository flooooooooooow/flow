#!/usr/bin/env bash
# Build & run the Schur all-pass DSP correctness tests (no JUCE needed).
set -euo pipefail
cd "$(dirname "$0")"

# Self-hosted runners may expose a missing TMPDIR or /tmp. Keep clang's
# temporary object files in an existing writable directory for this test.
clang_tmp="$(mktemp -d "${PWD}/.schur-clang-tmp.XXXXXX")"
trap 'rm -rf -- "$clang_tmp"' EXIT
export TMPDIR="$clang_tmp"

clang++ -O2 -std=c++17 dsp_test.cpp ../Source/SchurLatticeDSP.cpp -o dsp_test
./dsp_test
