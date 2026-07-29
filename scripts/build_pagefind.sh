#!/usr/bin/env bash
# Index the built wiki with Pagefind (optional — skips cleanly without node/npx).
#
# Usage (after wiki build):
#   python3 scripts/build_wiki.py          # calls this automatically
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
  echo "Pagefind skipped: $INDEX missing — run scripts/build_wiki.py first"
  exit 0
fi

echo "Building Pagefind index from search-index.json…"

python3 - "$INDEX" "$SRC" <<'PY'
import html
import json
import shutil
import sys
from pathlib import Path

index_path = Path(sys.argv[1])
src = Path(sys.argv[2])
if src.exists():
    shutil.rmtree(src)
src.mkdir(parents=True)

entries = json.loads(index_path.read_text(encoding="utf-8"))
for entry in entries:
    rel = entry.get("path") or ""
    if not rel:
        continue
    title = entry.get("title") or rel
    category = entry.get("category") or "guide"
    body = entry.get("text") or ""
    out = src / f"{rel}.html"
    out.parent.mkdir(parents=True, exist_ok=True)
    t = html.escape(title)
    c = html.escape(category)
    b = html.escape(body)
    out.write_text(
        f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>{t}</title>
</head>
<body>
<h1>{t}</h1>
<p data-pagefind-meta="category:{c}" data-pagefind-filter="category:{c}">{c}</p>
<main>{b}</main>
</body>
</html>
""",
        encoding="utf-8",
    )
print(f"  staged {len(entries)} HTML stubs → {src}")
PY

cleanup() {
  rm -rf "$SRC"
}
trap cleanup EXIT

if ! npx --yes pagefind --site "$SRC" --output-path "$OUT_PF"; then
  echo "Pagefind indexing failed — ⌘K will fall back to search-index.json" >&2
  rm -rf "$OUT_PF"
  exit 0
fi

echo "Pagefind ready → $OUT_PF"
