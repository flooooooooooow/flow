#!/usr/bin/env bash
# Build docs/demos/shaders.md from the canonical FSL gallery sources.
#
# The generator is the Flow program in scripts/tools/shader_gallery.
#
# Usage:
#   ./scripts/build_shader_gallery.sh
#   ./scripts/build_shader_gallery.sh --check [--check-assets]

set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

BIN="$(scripts/tools/build_tool.sh shader_gallery)"
exec "$BIN" "$@"
