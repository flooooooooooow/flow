#!/usr/bin/env bash
# Verify the Flow code examples embedded in the documentation.
#
# The checker is the Flow program in tools/doc_examples (see its main.flow
# for the commands). Flow cannot spawn git, so this shim lists the tracked
# markdown into build/doc-examples/, resolves the flowc the examples are
# compiled with (compiler/scripts/ensure_flowc.flow, as `flow compile` does),
# builds the checker from the checked-in bootstrap C, and runs it.
#
# Usage:
#   ./scripts/check_doc_examples.sh                    report
#   ./scripts/check_doc_examples.sh --check-ledger     fail on regressions (CI)
#   ./scripts/check_doc_examples.sh --write-ledger     refresh the ledger
#   ./scripts/check_doc_examples.sh --run              also run each program
#   ./scripts/check_doc_examples.sh strict             every block must pass
#   ./scripts/check_doc_examples.sh snippets           Flow hidden in text fences
#   ./scripts/check_doc_examples.sh lessons            tutorial lessons as JSON
#   ./scripts/check_doc_examples.sh blocks FILE...     fenced blocks as JSON
#   ./scripts/check_doc_examples.sh browser [--filter S] [--verbose] [--json F]
#                                          site/flow-compile.js against flowc
#
# --root DIR checks the markdown under DIR (tracked or not) instead of the
# repository; --ledger PATH names the ledger. Both are for tests.

set -euo pipefail

CALLER_PWD="$(pwd)"
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

OUT=build/doc-examples
mkdir -p "$OUT"
CC="${CC:-cc}"

# The checker, built by the checked-in Stage-A compiler.
BOOT_C=compiler/bootstrap/flowc_stage_a.c
TOOL_FLOWC="$OUT/flowc"
BIN="$ROOT/$OUT/doc_examples"
if [[ ! -x "$TOOL_FLOWC" || "$BOOT_C" -nt "$TOOL_FLOWC" ]]; then
    "$CC" -O1 -w -o "$TOOL_FLOWC.tmp.$$" "$BOOT_C" -lm
    mv -f "$TOOL_FLOWC.tmp.$$" "$TOOL_FLOWC"
fi
stale=0
if [[ ! -x "$BIN" || "$TOOL_FLOWC" -nt "$BIN" ]]; then
    stale=1
elif [[ -n "$(find tools/doc_examples scripts/tools/lib lib/stdlib compiler/src -name '*.flow' -newer "$BIN" -print -quit)" ]]; then
    stale=1
fi
if [[ "$stale" -eq 1 ]]; then
    if ! FLOWC_BUNDLE=1 FLOWC_DIR=. FLOWC_TYPECHECK=1 \
        FLOWC_IN=tools/doc_examples/main.flow FLOWC_OUT="$OUT/doc_examples.c" \
        "$TOOL_FLOWC" >"$OUT/doc_examples.flowc.log" 2>&1; then
        cat "$OUT/doc_examples.flowc.log" >&2
        echo "check_doc_examples: flowc could not compile tools/doc_examples/main.flow" >&2
        exit 1
    fi
    "$CC" -O2 -w -o "$BIN.tmp.$$" "$OUT/doc_examples.c" -lm
    mv -f "$BIN.tmp.$$" "$BIN"
fi

# The markdown to check: the git index, or every file under --root.
# Paths given as --root and --ledger are made absolute here, because the
# checker runs from the repository root.
docs_root="$ROOT"
args=()
prev=""
for arg in "$@"; do
    if [[ "$prev" == "--root" ]]; then
        arg="$(cd "$CALLER_PWD" && cd "$arg" && pwd)"
        docs_root="$arg"
    elif [[ ( "$prev" == "--ledger" || "$prev" == "--json" ) && "$arg" != /* ]]; then
        arg="$CALLER_PWD/$arg"
    fi
    args+=("$arg")
    prev="$arg"
done
listing="$OUT/markdown.$$.txt"
work="$(cd "$(mktemp -d "${TMPDIR:-/tmp}/flow-doc-examples.XXXXXX")" && pwd)"
trap 'rm -rf "$work" "$listing"' EXIT
if [[ "$docs_root" == "$ROOT" ]]; then
    git ls-files '*.md' > "$listing"
else
    (cd "$docs_root" && find . -name '*.md' -type f | sed 's#^\./##' | LC_ALL=C sort) > "$listing"
fi

# The compiler the examples go through: the one `flow compile` uses.
flowc="${FLOWC_BIN:-}"
if [[ -z "$flowc" || ! -x "$flowc" ]]; then
    flowc="$(./flow tool compiler/scripts/ensure_flowc.flow)"
fi
[[ "$flowc" == /* ]] || flowc="$ROOT/$flowc"

# `blocks FILE...` reads its files relative to where it was called from.
[[ "${1:-}" == "blocks" ]] && cd "$CALLER_PWD"
FLOW_DOC_REPO="$ROOT" FLOW_DOC_FLOWC="$flowc" FLOW_DOC_WORK="$work" \
    FLOW_DOC_LISTING="$listing" "$BIN" ${args[@]+"${args[@]}"}
