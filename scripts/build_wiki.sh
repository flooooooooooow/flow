#!/usr/bin/env bash
# Build the Flow wiki static site into build/wiki.
#
# The builder is the Flow program in scripts/tools/build_wiki. It refreshes
# docs/library/stdlib-api.md, copies docs/ and the proof corpus, validates
# docs/nav.json, writes the generated pages, the nav, the search index and
# the proof graph, then runs scripts/build_pagefind.sh unless
# FLOW_WIKI_SKIP_PAGEFIND is set.
#
# Usage:
#   ./scripts/build_wiki.sh

set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd -P)"
cd "$ROOT"

BIN="$(scripts/tools/build_tool.sh build_wiki)"
exec "$BIN" "$@"
