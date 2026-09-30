#!/usr/bin/env bash
# WebSocket echo relay (and optional plain TCP echo) for the WASM sockets
# demo. The relay is the Flow program in scripts/tools/ws_echo_relay, built
# with the Stage-A compiler on first use.
#
#   scripts/ws_echo_relay.sh --port 9505
#   scripts/ws_echo_relay.sh --port 9505 --tcp-port 9506 -v
#
# See docs/language/wasm-crossings.md.

set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd -P)"
BIN="$ROOT/$("$ROOT/scripts/tools/build_tool.sh" ws_echo_relay)"
exec "$BIN" "$@"
