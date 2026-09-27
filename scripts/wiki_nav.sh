#!/usr/bin/env bash
# Check docs/nav.json against docs/, the way the wiki build does.
#
# The checker is the Flow program in scripts/tools/wiki_nav.
#
# Usage:
#   ./scripts/wiki_nav.sh                  # summary; exit 1 on any problem
#   ./scripts/wiki_nav.sh --problems       # one problem per line
#   ./scripts/wiki_nav.sh --pages | --listed | --category PATH | --sections

set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd -P)"
cd "$ROOT"

BIN="$(scripts/tools/build_tool.sh wiki_nav)"
exec "$BIN" "$@"
