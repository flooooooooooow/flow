#!/usr/bin/env bash
# Parity gate for the dynamics DSL expander (compiler/src/dynamics_dsl.flow).
#
# The Flow port replaced src/flow/dynamics_dsl.py (with the corrections in
# src/flow/_dynamics_dsl_fixes.py applied). Its output was recorded from
# that Python reference as goldens beside each fixture in
# compiler/fixtures/dynamics_dsl/: `<name>.expected` for the expanded
# source, or `<name>.error` for the exception text. This gate holds flowc
# to them.
#
#   ./compiler/scripts/parity_dynamics_dsl.sh
#       flowc vs goldens, passthrough of every tracked .flow without the
#       DSL, then one DSL example end to end on flowc with python stubbed.
#
#   ./compiler/scripts/parity_dynamics_dsl.sh --python <rev>
#       also run the Python expander from git revision <rev> over the
#       fixtures and every tracked .flow, and require byte-identical output
#       (or error text) from flowc. Needs python3 and git.
#
#   ./compiler/scripts/parity_dynamics_dsl.sh --write-golden <rev>
#       rewrite the goldens from the Python expander at <rev>.
#
# The last Python revision is 7527ab37.
#
# Env: FLOWC_BIN=<path> tests that binary instead of building
# compiler/build/flowc_bootstrap from the checked-in bootstrap C.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
cd "$ROOT"

FIX=compiler/fixtures/dynamics_dsl
WORK=compiler/build/parity_dynamics_dsl
mode="${1:-}"
rev="${2:-}"
rm -rf "$WORK"
mkdir -p "$WORK/flowc" "$WORK/python"

if [[ -n "${FLOWC_BIN:-}" ]]; then
    BIN="$FLOWC_BIN"
else
    BIN=compiler/build/flowc_bootstrap
    "${CC:-cc}" -O2 -o "$BIN" compiler/bootstrap/flowc_stage_a.c -lm 2>/dev/null
fi
echo "=== parity_dynamics_dsl: flowc = ${BIN} ==="

fixtures=()
for f in "$FIX"/*.flow; do
    fixtures+=("$f")
done

golden_base() {
    printf '%s/%s\n' "$FIX" "$(basename "$1" .flow)"
}

# flowc_expand <in> <out.flow> <out.err>: expanded source, or the message.
flowc_expand() {
    local in="$1" out="$2" err="$3"
    rm -f "$out" "$err"
    local log code
    set +e
    log="$(FLOWC_EXPAND_ONLY=dynamics FLOWC_IN="$in" FLOWC_OUT="$out" "$BIN" 2>&1)"
    code=$?
    set -e
    if [[ "$code" -ne 0 ]]; then
        rm -f "$out"
        printf '%s\n' "$log" | sed -n '/^flowc dynamics: /,$p' | sed '1s/^flowc dynamics: //' > "$err"
        if [[ ! -s "$err" ]]; then
            printf 'flowc failed without a dynamics diagnostic: %s\n' "$log" > "$err"
        fi
    fi
}

# python_expand <rev> <list-file> <outdir>: run the Python reference at <rev>.
python_expand() {
    local r="$1" list="$2" outdir="$3"
    local pkg="$WORK/pyref/dynref"
    mkdir -p "$pkg"
    : > "$pkg/__init__.py"
    git show "${r}:src/flow/dynamics_dsl.py" > "$pkg/dynamics_dsl.py"
    git show "${r}:src/flow/_dynamics_dsl_fixes.py" > "$pkg/_dynamics_dsl_fixes.py"
    python3 - "$WORK/pyref" "$list" "$outdir" <<'PY'
import os, sys
sys.path.insert(0, sys.argv[1])
from dynref import _dynamics_dsl_fixes as fixes
from dynref import dynamics_dsl as dsl
fixes.install()
outdir = sys.argv[3]
for path in open(sys.argv[2]).read().split("\n"):
    if not path:
        continue
    key = path.replace("/", "__")
    with open(path, encoding="utf-8", newline="") as f:
        text = f.read()
    try:
        out = dsl.expand_dynamics_dsl(text)
    except Exception as e:
        with open(os.path.join(outdir, key + ".err"), "w", encoding="utf-8", newline="") as f:
            f.write(str(e) + "\n")
        continue
    with open(os.path.join(outdir, key + ".flow"), "w", encoding="utf-8", newline="") as f:
        f.write(out)
PY
}

if [[ "$mode" == "--write-golden" ]]; then
    [[ -n "$rev" ]] || { echo "usage: $0 --write-golden <rev>" >&2; exit 2; }
    printf '%s\n' "${fixtures[@]}" > "$WORK/fixtures.txt"
    python_expand "$rev" "$WORK/fixtures.txt" "$WORK/python"
    for f in "${fixtures[@]}"; do
        key="${f//\//__}"
        base="$(golden_base "$f")"
        rm -f "$base.expected" "$base.error"
        if [[ -f "$WORK/python/$key.err" ]]; then
            cp "$WORK/python/$key.err" "$base.error"
        else
            cp "$WORK/python/$key.flow" "$base.expected"
        fi
    done
    echo "wrote goldens for ${#fixtures[@]} fixtures from ${rev}"
    exit 0
fi

fail=0
pass=0

# 1. Fixtures vs goldens.
for f in "${fixtures[@]}"; do
    key="${f//\//__}"
    base="$(golden_base "$f")"
    flowc_expand "$f" "$WORK/flowc/$key.flow" "$WORK/flowc/$key.err"
    if [[ -f "$base.error" ]]; then
        if [[ -f "$WORK/flowc/$key.err" ]] && cmp -s "$base.error" "$WORK/flowc/$key.err"; then
            pass=$((pass + 1))
        else
            fail=$((fail + 1))
            echo "FAIL $f: want error: $(cat "$base.error")" >&2
            [[ -f "$WORK/flowc/$key.err" ]] && echo "     got error:  $(cat "$WORK/flowc/$key.err")" >&2
        fi
    elif [[ -f "$base.expected" ]]; then
        if [[ -f "$WORK/flowc/$key.flow" ]] && cmp -s "$base.expected" "$WORK/flowc/$key.flow"; then
            pass=$((pass + 1))
        else
            fail=$((fail + 1))
            echo "FAIL $f: expansion differs from $base.expected" >&2
            if [[ -f "$WORK/flowc/$key.flow" ]]; then
                diff "$base.expected" "$WORK/flowc/$key.flow" | head -20 >&2 || true
            else
                echo "     flowc error: $(cat "$WORK/flowc/$key.err")" >&2
            fi
        fi
    else
        fail=$((fail + 1))
        echo "FAIL $f: no golden (.expected or .error)" >&2
    fi
done
echo "fixtures: pass=${pass} fail=${fail}"

# 2. Every tracked .flow: DSL files must match their golden (checked via
# --python); every other file must pass through untouched.
git ls-files '*.flow' | grep -v "^${FIX}/" | LC_ALL=C sort > "$WORK/corpus.txt"
corpus_n=0
dsl_n=0
corpus_fail=0
while IFS= read -r f; do
    [[ -f "$f" ]] || continue
    key="${f//\//__}"
    flowc_expand "$f" "$WORK/flowc/$key.flow" "$WORK/flowc/$key.err"
    if [[ -f "$WORK/flowc/$key.flow" ]] && cmp -s "$f" "$WORK/flowc/$key.flow"; then
        corpus_n=$((corpus_n + 1))
    else
        dsl_n=$((dsl_n + 1))
        echo "$f" >> "$WORK/dsl_files.txt"
    fi
done < "$WORK/corpus.txt"
echo "passthrough: files=${corpus_n} (dsl files expanded: ${dsl_n})"

# 3. Optional: live diff against the Python reference at <rev>.
if [[ "$mode" == "--python" ]]; then
    [[ -n "$rev" ]] || { echo "usage: $0 --python <rev>" >&2; exit 2; }
    { printf '%s\n' "${fixtures[@]}"; cat "$WORK/corpus.txt"; } > "$WORK/all.txt"
    python_expand "$rev" "$WORK/all.txt" "$WORK/python"
    live_n=0
    live_fail=0
    while IFS= read -r f; do
        [[ -n "$f" && -f "$f" ]] || continue
        key="${f//\//__}"
        live_n=$((live_n + 1))
        if [[ -f "$WORK/python/$key.err" ]]; then
            if ! cmp -s "$WORK/python/$key.err" "$WORK/flowc/$key.err" 2>/dev/null; then
                live_fail=$((live_fail + 1))
                echo "FAIL live $f: python error differs" >&2
            fi
        elif ! cmp -s "$WORK/python/$key.flow" "$WORK/flowc/$key.flow" 2>/dev/null; then
            live_fail=$((live_fail + 1))
            echo "FAIL live $f: python output differs" >&2
        fi
    done < "$WORK/all.txt"
    echo "live python@${rev}: files=${live_n} fail=${live_fail}"
    fail=$((fail + live_fail))
else
    # Without Python, a DSL file in the corpus must be one of the fixtures'
    # sources (examples are mirrored as ex_* fixtures).
    if [[ -f "$WORK/dsl_files.txt" ]]; then
        while IFS= read -r f; do
            mirror="$FIX/ex_$(basename "$f")"
            if [[ ! -f "$mirror" ]] || ! cmp -s "$f" "$mirror"; then
                fail=$((fail + 1))
                echo "FAIL corpus $f: expanded, but no ex_ fixture mirrors it" >&2
            fi
        done < "$WORK/dsl_files.txt"
    fi
fi

# 4. End to end: a DSL program compiles on flowc alone and runs clean, with
# python and python3 stubbed out on PATH so any call would fail.
# FLOWC_TYPECHECK=0: the dynamics stdlib calls functions it does not
# export, which the Python host allows and flowc's bundle typecheck does
# not yet (#988). The emitted C is complete; only the check is skipped.
E2E=examples/dynamics/ga_dsys_syntax.flow
export FLOWC_TYPECHECK=0
mkdir -p "$WORK/nopy"
printf '#!/bin/sh\necho "python called: $*" >> "%s/nopy/calls.log"\nexit 127\n' "$ROOT/$WORK" > "$WORK/nopy/python3"
cp "$WORK/nopy/python3" "$WORK/nopy/python"
chmod +x "$WORK/nopy/python3" "$WORK/nopy/python"
set +e
PATH="$ROOT/$WORK/nopy:$PATH" FLOWC_BUNDLE=1 FLOWC_DIR=. FLOWC_IN="$E2E" FLOWC_OUT="$WORK/e2e.c" \
    "$BIN" >"$WORK/e2e_emit.log" 2>&1
set -e
if [[ -s "$WORK/e2e.c" ]] && "${CC:-cc}" -O1 -w -o "$WORK/e2e" "$WORK/e2e.c" -lm 2>"$WORK/e2e_cc.log"; then
    set +e
    PATH="$ROOT/$WORK/nopy:$PATH" "$WORK/e2e" > "$WORK/e2e_run.log" 2>&1
    code=$?
    set -e
    if [[ "$code" -eq 0 && ! -s "$WORK/nopy/calls.log" ]]; then
        echo "e2e: $(basename "$E2E") exit 0 on flowc, no python call"
    else
        fail=$((fail + 1))
        echo "FAIL e2e: $(basename "$E2E") exit ${code}" >&2
        tail -5 "$WORK/e2e_run.log" >&2
        cat "$WORK/nopy/calls.log" 2>/dev/null >&2 || true
    fi
else
    fail=$((fail + 1))
    echo "FAIL e2e: $(basename "$E2E") did not build on flowc" >&2
    cat "$WORK/e2e_emit.log" "$WORK/e2e_cc.log" 2>/dev/null | head -20 >&2
fi

if [[ "$fail" -ne 0 ]]; then
    echo "parity_dynamics_dsl: FAIL (${fail})"
    exit 1
fi
echo "parity_dynamics_dsl: PASS"
