#!/usr/bin/env bash
# Record docs/demos/*.gif by running the real Flow programs headlessly.
#
#   scripts/record_demos.sh            # all demos
#   scripts/record_demos.sh lorenz     # one demo
#   scripts/record_demos.sh --group morphogenesis
#   scripts/record_demos.sh --group neuro
#   scripts/record_demos.sh --group evoleco
#   scripts/record_demos.sh --group planet
#   scripts/record_demos.sh --group procgen
#   scripts/record_demos.sh --group numerical
#   scripts/record_demos.sh --check    # every GIF present?
#
# The recorder is the Flow program in scripts/tools/record_demos, built with
# the Stage-A compiler on first use. The demo table and the input scripts
# live there. Each clip is recorded with `./flow record` and encoded by
# scripts/tools/lib/gifclip.flow. No Python.

set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd -P)"
BIN="$("$ROOT/scripts/tools/build_tool.sh" record_demos)"
FLOW_REPO_ROOT="$ROOT" exec "$ROOT/$BIN" "$@"
