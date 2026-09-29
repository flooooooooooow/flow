#!/usr/bin/env bash
# Verify that every .flow file under examples/ (and apps/, benchmarks/)
# compiles, and regenerate the status table in examples/STATUS.md.
#
# The logic is the Flow program in scripts/tools/verify_examples. It runs the
# Python transpiler and clang per file, in parallel through xargs -P.
#
# Usage (from anywhere):
#   ./scripts/verify_examples.sh                 # sweep + rewrite examples/STATUS.md
#   ./scripts/verify_examples.sh --roots examples
#   ./scripts/verify_examples.sh --json out.json --no-write
#
# Set VERIFY_PYTHON to choose the interpreter for the transpiler (default
# python3).

set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd -P)"

BIN="$ROOT/$("$ROOT/scripts/tools/build_tool.sh" verify_examples)"
VERIFY_ROOT="$ROOT" exec "$BIN" "$@"
