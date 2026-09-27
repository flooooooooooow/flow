#!/usr/bin/env bash
# Does the documentation cover every part of the language?
#
# The checker is the Flow program in scripts/tools/doc_coverage. Flow cannot
# spawn git or list directories, so the listings it needs are written to
# build/doc-coverage/ here first.
#
# Usage:
#   ./scripts/check_doc_coverage.sh                   # report and gate
#   ./scripts/check_doc_coverage.sh --propose         # suggest homes for gaps
#   ./scripts/check_doc_coverage.sh --write-proposal  # rewrite docs/coverage.json

set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

BIN="$(scripts/tools/build_tool.sh doc_coverage)"

OUT=build/doc-coverage
mkdir -p "$OUT"
git ls-files 'lib/stdlib/*.flow' 'lib/stdlib/**/*.flow' > "$OUT/stdlib.txt"
find src/flow -maxdepth 1 -name '*.py' > "$OUT/backends.txt"
find docs -name '*.md' > "$OUT/doc-pages.txt"

exec "$BIN" "$@"
