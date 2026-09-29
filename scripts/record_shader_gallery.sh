#!/usr/bin/env bash
# Record FSL shaders to GIFs through the real Metal backend.
#
#   ./scripts/record_shader_gallery.sh --group photoreal
#   ./scripts/record_shader_gallery.sh --name photoreal_gold
#   ./scripts/record_shader_gallery.sh --group classic --frames 30 --fps 15
#
# The recorder is the Flow program in scripts/tools/shader_record, built with
# the Stage-A compiler on first use. It runs scripts/frames_to_gif.py, which
# needs python3 with Pillow, to encode each GIF.

set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd -P)"
BIN="$("$ROOT/scripts/tools/build_tool.sh" shader_record)"
FLOW_REPO_ROOT="$ROOT" exec "$ROOT/$BIN" "$@"
