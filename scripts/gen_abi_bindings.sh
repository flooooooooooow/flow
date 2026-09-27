#!/usr/bin/env bash
# Generate C and Flow bindings from a .abi file.
#
# The generator is the Flow program in scripts/tools/abi_bindings. Paths are
# taken relative to the caller's directory.
#
# Usage:
#   ./scripts/gen_abi_bindings.sh demos/vulkan_abi/renderer.abi [--out-dir DIR]

set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"

BIN="$ROOT/$("$ROOT/scripts/tools/build_tool.sh" abi_bindings)"
exec "$BIN" "$@"
