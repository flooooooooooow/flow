#!/usr/bin/env bash
# Serve a directory over HTTP on 127.0.0.1 for local previews.
#
#   ./scripts/wiki_serve.sh                   # build/wiki on port 8899
#   ./scripts/wiki_serve.sh build/wiki 8777
#   ./scripts/wiki_serve.sh site 8000
#
# GET and HEAD only; a directory serves its index.html. Stop it with Ctrl-C.
# The server is the `serve` mode of the Flow program in
# scripts/tools/wiki_browser.

set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd -P)"
if [[ $# -gt 2 ]]; then
  echo "usage: scripts/wiki_serve.sh [DIR] [PORT]" >&2
  exit 2
fi
# shellcheck source=scripts/tools/wiki_browser/env.sh
# shellcheck disable=SC1091 # shared env, checked on its own
source "$ROOT/scripts/tools/wiki_browser/env.sh"
exec "$WIKI_BROWSER_BIN" serve "${1:-$ROOT/build/wiki}" "${2:-8899}"
