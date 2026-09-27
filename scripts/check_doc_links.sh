#!/usr/bin/env bash
# Check that relative links in tracked markdown resolve to tracked files.
#
# The checker is the Flow program in scripts/tools/doc_links. Flow cannot
# spawn git, so `git ls-files` runs here and leaves its output in
# build/doc-links/ for the Flow program to read.
#
# Usage:
#   ./scripts/check_doc_links.sh            # report and exit 1 on breakage
#   ./scripts/check_doc_links.sh --list-ok  # also list what was skipped
#   ./scripts/check_doc_links.sh --slug "Some Heading"
#   ./scripts/check_doc_links.sh --anchors docs/LANGUAGE_SPEC.md

set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

BIN="$(scripts/tools/build_tool.sh doc_links)"

mkdir -p build/doc-links
git ls-files > build/doc-links/tracked.txt
git ls-files '*.md' > build/doc-links/markdown.txt

exec "$BIN" "$@"
