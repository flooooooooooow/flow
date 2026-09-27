#!/usr/bin/env bash
# Check a Flow challenge submission: required syntax first, then compile and
# run it. The checker is the Flow program in scripts/tools/challenge_check.
#
#   challenges/flow-specific/check.sh list
#   challenges/flow-specific/check.sh check F01 answer.flow [--syntax-only] [--timeout N]
#   challenges/flow-specific/check.sh scan file.flow...
#   challenges/flow-specific/check.sh self-test

set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
BIN="$("$ROOT/scripts/tools/build_tool.sh" challenge_check)"
FLOW_REPO_ROOT="$ROOT" exec "$ROOT/$BIN" "$@"
