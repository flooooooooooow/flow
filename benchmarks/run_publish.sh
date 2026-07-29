#!/bin/bash
# Regenerates benchmarks/RESULTS.md. Run from anywhere in the repo.
set -e
cd "$(dirname "$0")/.."
PYTHONPATH=src python3 benchmarks/run_publish.py "$@"
