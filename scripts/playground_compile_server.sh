#!/usr/bin/env bash
# Local native compile API for the Flow playground (GitHub #132, Option B).
#
# Binds to 127.0.0.1. The playground's "Run (native local)" button POSTs
# source here; the server transpiles it with flowc, optionally compiles and
# runs it with clang, and returns stdout/stderr. The server is the Flow
# program in scripts/tools/playground_server, built with the Stage-A
# compiler on first use; its header lists the routes and security limits.
#
#   scripts/playground_compile_server.sh
#   scripts/playground_compile_server.sh --port 8765 --no-run   # transpile only
#   ./flow playground [PORT]

set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd -P)"
BIN="$ROOT/$("$ROOT/scripts/tools/build_tool.sh" playground_server)"
export FLOW_REPO_ROOT="$ROOT"
exec "$BIN" "$@"
