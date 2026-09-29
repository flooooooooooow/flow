#!/usr/bin/env bash
# Compile Flow or LLVM IR to an eBPF ELF object (little-endian, bpfel).
#
#   scripts/bpf_target.sh IN.flow|IN.ll -o OUT.o [--entry NAME --section SEC]
#       [--license TEXT] [-O 0|1|2|3]
#
# The compiler is the Flow program in scripts/tools/llvm_target, built with
# the Stage-A compiler on first use. `flow bpf` runs this. Flow sources reach
# LLVM IR through compiler/scripts/flow_to_llvm.sh.

set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd -P)"
BIN="$("$ROOT/scripts/tools/build_tool.sh" llvm_target)"
[[ "$BIN" == /* ]] || BIN="$ROOT/$BIN"
FLOW_REPO_ROOT="$ROOT" exec "$BIN" bpf "$@"
