#!/usr/bin/env bash
# Golden check for `flow check` (tools/check/main.flow).
#
# The goldens in tests/check/expect were recorded from the retired Python
# implementation (src/flow/check.py, conventions.py, idioms.py): stdout,
# stderr and the exit status of each case below. Each case runs in a fresh
# copy of a fixture project under $TMPDIR, where the *.flow.in sources become
# *.flow (they stay out of the repository's .flow corpus that way). The copy
# also gets the things git cannot hold: a build/ and a .freebuff/ file (both
# skipped), a directory named dir.flow, a symlink to a source file and a
# symlink to a directory (not descended). The temporary path is written as
# ROOT in the goldens.
#
# Cases without file arguments list the files in Path.rglob order, which is
# the directory order of the file system (os.scandir), so those cases compare
# sorted lines. Cases with file arguments compare exactly.
#
# Runs with python and python3 stubbed out.
#
# Usage:
#   tests/check/run.sh
#   FLOW_CHECK_REF='<command>' tests/check/run.sh --record   # rewrite goldens

set -euo pipefail

ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
cd "$ROOT"
HERE="$ROOT/tests/check"
EXPECT="$HERE/expect"

record=0
[[ "${1:-}" == "--record" ]] && record=1

work="$(mktemp -d "${TMPDIR:-/tmp}/flow-check.XXXXXX")"
trap 'rm -rf "$work"' EXIT

if [[ "$record" -eq 1 ]]; then
    cmd="${FLOW_CHECK_REF:?set FLOW_CHECK_REF to the reference command}"
    mkdir -p "$EXPECT"
else
    tool="$("$ROOT/flow-driver" check --build)"
    cmd="$tool"
    mkdir -p "$work/bin"
    for name in python python3; do
        printf '#!/bin/sh\necho "%s called: $*" >&2\nexit 127\n' "$name" > "$work/bin/$name"
        chmod +x "$work/bin/$name"
    done
    export PATH="$work/bin:$PATH"
fi

# Fresh copy of fixture $1 at $work/run/$1; prints the physical path.
setup() {
    local fx="$1"
    rm -rf "$work/run"
    mkdir -p "$work/run"
    cp -R "$HERE/fixtures/$fx" "$work/run/$fx"
    local d="$work/run/$fx"
    local f
    while IFS= read -r f; do
        mv "$f" "${f%.in}"
    done < <(find "$d" -name '*.flow.in')
    if [[ "$fx" == "proj" ]]; then
        mkdir -p "$d/build" "$d/.freebuff" "$d/dir.flow"
        printf 'function b() -> i32 {\n    let mut hidden: i32 = 1\n    return hidden\n}\n' > "$d/build/skipped.flow"
        cp "$d/build/skipped.flow" "$d/.freebuff/skipped.flow"
        ln -s src/idioms_basic.flow "$d/link.flow"
        ln -s src/nested "$d/linkdir"
    fi
    (cd "$d" && pwd -P)
}

pass=0
fail=0

# run_case NAME FIXTURE SUBDIR MODE ARGS...
run_case() {
    local name="$1" fx="$2" sub="$3" mode="$4"
    shift 4
    local d
    d="$(setup "$fx")"
    local rc=0
    (cd "$d/$sub" && $cmd "$@" > "$work/out" 2> "$work/err") || rc=$?
    local o
    for o in out err; do
        sed "s#$d#ROOT#g" "$work/$o" > "$work/$o.n"
        if [[ "$mode" == "sorted" ]]; then
            LC_ALL=C sort "$work/$o.n" > "$work/$o.s"
            mv "$work/$o.s" "$work/$o.n"
        fi
    done
    echo "$rc" > "$work/rc.n"
    if [[ "$record" -eq 1 ]]; then
        cp "$work/out.n" "$EXPECT/$name.stdout"
        cp "$work/err.n" "$EXPECT/$name.err"
        cp "$work/rc.n" "$EXPECT/$name.rc"
        echo "recorded $name (exit $rc)"
        return
    fi
    if cmp -s "$work/out.n" "$EXPECT/$name.stdout" && cmp -s "$work/err.n" "$EXPECT/$name.err" \
            && cmp -s "$work/rc.n" "$EXPECT/$name.rc"; then
        pass=$((pass + 1))
    else
        fail=$((fail + 1))
        echo "FAIL $name"
        diff "$EXPECT/$name.stdout" "$work/out.n" | head -10 || true
        diff "$EXPECT/$name.err" "$work/err.n" | head -10 || true
        diff "$EXPECT/$name.rc" "$work/rc.n" || true
    fi
}

files=(src/idioms_basic.flow src/flowblock.flow src/crlf.flow src/idioms_if.flow
       src/nested/idioms_match.flow src/nested/parse_error.flow src/bad_utf8.flow
       dir.flow link.flow ./src//idioms_basic.flow missing.flow)

run_case avoid_rglob          proj    .           sorted
run_case idioms_rglob         proj    .           sorted --idioms
run_case idioms_json_rglob    proj    .           sorted --idioms --format=json
run_case avoid_json           proj    .           sorted --format=json
run_case idioms_text_files    proj    .           exact  -v --idioms "${files[@]}"
run_case idioms_json_files    proj    .           exact  --idioms --format=json "${files[@]}"
run_case idioms_xml_files     proj    .           exact  --idioms --format=xml src/idioms_basic.flow src/idioms_if.flow
run_case format_space         proj    .           exact  --format json
run_case avoid_files          proj    .           exact  src/idioms_basic.flow src/nested/idioms_match.flow missing.flow
run_case nested_cwd           proj    src/nested  sorted
run_case clean_files          proj    .           exact  src/crlf.flow
run_case clean_idioms         proj    .           exact  --idioms src/idioms_if.flow
run_case inline_rglob         inline  .           sorted
run_case noconv               noconv  .           exact
run_case noconv_idioms        noconv  .           sorted --idioms
run_case badtoml              badtoml .           exact
run_case badtoml_idioms       badtoml .           exact  --idioms a.flow
run_case no_flow_files        empty   .           exact

if [[ "$record" -eq 0 ]]; then
    echo "flow check: pass=$pass fail=$fail"
    [[ "$fail" -eq 0 ]]
fi
