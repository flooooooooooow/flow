#!/usr/bin/env bash
# Encode recorded PPM frames into an animated GIF.
#
#   scripts/frames_to_gif.sh <frame-dir> <out.gif> [--fps 20] [--stride 2] [--width 480]
#
# Used by `flow record --gif`, which passes --fps/--stride/--width straight
# through. The encoder is the Flow program in scripts/tools/frames_to_gif,
# built with the Stage-A compiler on first use. No Python.

set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd -P)"
BIN="$("$ROOT/scripts/tools/build_tool.sh" frames_to_gif)"
exec "$ROOT/$BIN" "$@"
