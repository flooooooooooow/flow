#!/usr/bin/env bash
# Validate internal links in the built wiki (run scripts/build_wiki.sh first).
#
# The checker is the Flow program in scripts/tools/wiki_links. Flow cannot
# list directories, so find(1) runs here and leaves the tree listing in
# build/wiki-links/ for the Flow program to read.
#
# Usage:
#   ./scripts/check_wiki_links.sh

set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

BIN="$(scripts/tools/build_tool.sh wiki_links)"

mkdir -p build/wiki-links
if [[ -d build/wiki ]]; then
  find build/wiki > build/wiki-links/entries.txt
  find build/wiki -type d > build/wiki-links/dirs.txt
fi

exec "$BIN" "$@"
