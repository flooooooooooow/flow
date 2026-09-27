#!/usr/bin/env bash
# Gradient code generation for a scalar f32 Flow function.
#
#   scripts/tools/grad/grad.sh c    <file.flow> <function> > out.c
#   scripts/tools/grad/grad.sh flow <file.flow> <function> > out.flow
#
# The generator is the Flow program next to this script, built with the
# Stage-A compiler on first use.

set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../../.." && pwd)"
BIN="$("$ROOT/scripts/tools/build_tool.sh" grad)"
exec "$ROOT/$BIN" "$@"
