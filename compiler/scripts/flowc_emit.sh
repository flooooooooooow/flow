#!/usr/bin/env bash
# Compile one Flow program to C with flowc, the way `flow compile` does.
#
#   compiler/scripts/flowc_emit.sh [--strict|--lenient] [--no-checks]
#       [--library] [--export NAME]... [--module-name NAME] IN.flow OUT.c
#
# This is the one C path for scripts and tools. It replaces
# `python3 -m flow.transpiler IN --c -o OUT`, which is retired.
#
# Defaults match `flow compile`: the type checker runs, type errors are
# warnings except the ones that stay fatal (--lenient, FLOWC_LENIENT=1), and
# the runtime checks for division, shifts and array bounds are emitted
# (FLOWC_CHECKS=1). --strict makes every type error fatal, as the old
# `--strict`. --no-checks leaves the runtime checks out, as the old
# `--no-bounds-check`.
#
# --library (FLOWC_LIBRARY=1) emits a unit to link next to a program, as the
# old `--library`: no runtime checks, no fault handler, plain C names with
# external linkage, and no main needed. --export NAME (repeatable, or a comma
# list; FLOWC_EXPORT="a,b") appends a visible `flow_export_NAME` alias for
# each function, as the old `--export` (#1030). --module-name is accepted for
# the old command lines; as before, it does not change the C.
#
# A program that imports modules, or uses the Field or dynamics DSL, is
# bundled into one C unit from the repository root, so `stdlib/...` imports
# resolve against lib/stdlib and path imports against the repository.
#
# The compiler is FLOWC_BIN when set, else compiler/scripts/ensure_flowc.sh.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/../.." && pwd)"

lenient="${FLOWC_LENIENT:-1}"
checks="${FLOWC_CHECKS:-1}"
library="${FLOWC_LIBRARY:-0}"
exports="${FLOWC_EXPORT:-}"
while [[ $# -gt 0 ]]; do
    case "$1" in
        --strict) lenient=0; shift ;;
        --lenient) lenient=1; shift ;;
        --no-checks) checks=0; shift ;;
        --library) library=1; shift ;;
        --export)
            [[ $# -ge 2 ]] || { echo "flowc_emit: --export needs a NAME" >&2; exit 2; }
            exports="${exports:+$exports,}$2"; shift 2 ;;
        --export=*) exports="${exports:+$exports,}${1#--export=}"; shift ;;
        --module-name)
            [[ $# -ge 2 ]] || { echo "flowc_emit: --module-name needs a NAME" >&2; exit 2; }
            shift 2 ;;
        --module-name=*) shift ;;
        --) shift; break ;;
        -*) echo "flowc_emit: unknown option $1" >&2; exit 2 ;;
        *) break ;;
    esac
done
if [[ $# -ne 2 ]]; then
    echo "usage: flowc_emit.sh [--strict|--lenient] [--no-checks] [--library] [--export NAME]... IN.flow OUT.c" >&2
    exit 2
fi
program="$1"
c_out="$2"
if [[ ! -f "$program" ]]; then
    echo "flowc_emit: no such file: $program" >&2
    exit 1
fi

driver="${FLOWC_BIN:-}"
if [[ -z "$driver" || ! -x "$driver" ]]; then
    driver="$(bash "$ROOT/compiler/scripts/ensure_flowc.sh")" || {
        echo "flowc_emit: no flowc (set FLOWC_BIN or run compiler/scripts/bootstrap_from_c.sh)" >&2
        exit 1
    }
    [[ "$driver" == /* ]] || driver="$ROOT/$driver"
fi
case "$driver" in
    /*) ;;
    *) driver="$(cd "$(dirname "$driver")" && pwd)/$(basename "$driver")" ;;
esac

if [[ "$library" == 1 ]]; then
    checks=0
fi

mkdir -p "$(dirname "$c_out")"
abs_program="$(cd "$(dirname "$program")" && pwd)/$(basename "$program")"
abs_out="$(cd "$(dirname "$c_out")" && pwd)/$(basename "$c_out")"

if grep -Eq '^[[:space:]]*import[[:space:]]' "$program" || \
    grep -Eq '^[[:space:]]*(field|boundary)[[:space:]]' "$program" || \
    grep -Eq '^[[:space:]]*((dyn|dynamics)\.)?(dsys|horizon|sense|ga|closed|analyze|wfc|couple|guide|represent)[[:space:]]|^[[:space:]]*(dyn|dynamics)[[:space:]]*\{' "$program"; then
    cd "$ROOT"
    exec env FLOWC_BUNDLE=1 FLOWC_DIR="$ROOT" \
        FLOWC_TYPECHECK="${FLOWC_TYPECHECK:-1}" FLOWC_CHECKS="$checks" FLOWC_LENIENT="$lenient" \
        FLOWC_LIBRARY="$library" FLOWC_EXPORT="$exports" \
        FLOWC_IN="$abs_program" FLOWC_OUT="$abs_out" "$driver"
fi
# Positional argv runs the self-test; emit needs FLOWC_IN / FLOWC_OUT.
exec env -u FLOWC_BUNDLE \
    FLOWC_TYPECHECK="${FLOWC_TYPECHECK:-1}" FLOWC_CHECKS="$checks" FLOWC_LENIENT="$lenient" \
    FLOWC_LIBRARY="$library" FLOWC_EXPORT="$exports" \
    FLOWC_IN="$program" FLOWC_OUT="$c_out" "$driver"
