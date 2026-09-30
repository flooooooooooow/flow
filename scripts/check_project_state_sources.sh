#!/usr/bin/env bash
# Reject duplicate mutable project-state documents at the repository root.
#
# Questions.md, ROADMAP-1.0.md and RELEASE-1.0.md are short compatibility
# pointers to docs/project/Questions.md and the docs/project/archive/ copies.
# The checker is the Flow program in scripts/tools/project_state.
#
# Usage: ./scripts/check_project_state_sources.sh
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

BIN="$(scripts/tools/build_tool.sh project_state)"
exec "$BIN" "$@"
