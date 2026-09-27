#!/usr/bin/env bash
# Index the built wiki with Pagefind (optional; skips cleanly without node/npx).
#
# Usage (after wiki build):
#   ./scripts/build_wiki.sh                # calls this automatically
#   ./scripts/build_pagefind.sh            # standalone re-index
#
# Requires: node + npx. Writes build/wiki/pagefind/ for the ⌘K search UI.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
SITE="${FLOW_WIKI_OUT:-$ROOT/build/wiki}"
INDEX="$SITE/search-index.json"
SRC="$SITE/_pagefind_src"
OUT_PF="$SITE/pagefind"

if ! command -v node >/dev/null 2>&1 || ! command -v npx >/dev/null 2>&1; then
  echo "Pagefind skipped: node/npx not available (⌘K keeps using search-index.json)"
  exit 0
fi

if [[ ! -f "$INDEX" ]]; then
  echo "Pagefind skipped: $INDEX missing. Run scripts/build_wiki.sh first."
  exit 0
fi

echo "Building Pagefind index from search-index.json…"

# Pagefind writes one fragment file per indexed page. The flow-verify proof
# corpus is over a thousand pages, which pushed the deployed site past 2900
# files and made the GitHub Pages publish step time out. Proofs stay on the
# site and stay in search-index.json (the fallback search still finds them
# by title); they are simply not full-text indexed. The stubs are written by
# the Flow wiki builder.
BIN="$ROOT/$("$ROOT/scripts/tools/build_tool.sh" build_wiki)"
"$BIN" --pagefind-stage "$INDEX" "$SRC"

cleanup() {
  rm -rf "$SRC"
}
trap cleanup EXIT

if ! npx --yes pagefind --site "$SRC" --output-path "$OUT_PF"; then
  echo "Pagefind indexing failed; ⌘K will fall back to search-index.json" >&2
  rm -rf "$OUT_PF"
  exit 0
fi

echo "Pagefind ready → $OUT_PF"
