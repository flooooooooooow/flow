#!/usr/bin/env bash
# Regenerate docs/library/stdlib-api.md from lib/stdlib/*.flow exports.
#
# The generator is the Flow program in scripts/tools/gen_stdlib_docs.
# scripts/build_wiki.sh runs the same code before every wiki build.
#
# Usage:
#   ./scripts/gen_stdlib_docs.sh

set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd -P)"
cd "$ROOT"

BIN="$(scripts/tools/build_tool.sh gen_stdlib_docs)"
exec "$BIN" "$@"
