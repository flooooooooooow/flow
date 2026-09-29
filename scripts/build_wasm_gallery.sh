#!/usr/bin/env bash
# Compile a list of Flow examples to WebAssembly and build the gallery.
#
#   scripts/build_wasm_gallery.sh                          everything
#   scripts/build_wasm_gallery.sh --only snake_gfx gray_scott
#   scripts/build_wasm_gallery.sh --category games
#   scripts/build_wasm_gallery.sh --list
#
# Every target becomes site/wasm/<name>/ with its .wasm, .js loader and page,
# plus site/wasm/manifest.json and the gallery index.html. Examples that fail
# stay in the manifest with their error. The builder is the Flow program in
# scripts/tools/wasm_build.

set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd -P)"
# shellcheck source=scripts/tools/wasm_build/env.sh
# shellcheck disable=SC1091 # shared env, checked on its own
source "$ROOT/scripts/tools/wasm_build/env.sh"
exec "$WASM_BUILD_BIN" gallery "$@"
