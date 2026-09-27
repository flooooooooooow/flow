#!/usr/bin/env bash
# Parity gate for the Field DSL expander (compiler/src/field_dsl.flow).
#
# The Flow port replaced src/flow/field_dsl.py. Its output was recorded from
# that Python reference as goldens beside each fixture in
# compiler/fixtures/field_dsl/: `<name>.expected` for the expanded source, or
# `<name>.error` for the SyntaxError text. This gate holds flowc to them.
#
#   ./compiler/scripts/parity_field_dsl.sh
#       flowc vs goldens, passthrough of every non-DSL .flow in the repo,
#       then heat_diffusion end to end (flowc bundle, cc, run, exit 0).
#
#   ./compiler/scripts/parity_field_dsl.sh --python <rev>
#       also run the original Python expander from git revision <rev> over
#       the fixtures and every .flow under examples/, tests/ and lib/, and
#       require byte-identical output from flowc. Needs python3 and git.
#
#   ./compiler/scripts/parity_field_dsl.sh --write-golden <rev>
#       rewrite the goldens from the Python expander at <rev>.
#
# The last Python revision is 3dbbac87 (origin/main before the port).
#
# Env: FLOWC_BIN=<path> tests that binary instead of building
# compiler/build/flowc_bootstrap from the checked-in bootstrap C.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
cd "$ROOT"

FIX=compiler/fixtures/field_dsl
WORK=compiler/build/parity_field_dsl
mode="${1:-}"
rev="${2:-}"
rm -rf "$WORK"
mkdir -p "$WORK/flowc" "$WORK/python"

if [[ -n "${FLOWC_BIN:-}" ]]; then
    BIN="$FLOWC_BIN"
else
    BIN=compiler/build/flowc_bootstrap
    "${CC:-cc}" -O2 -o "$BIN" compiler/bootstrap/flowc_stage_a.c 2>/dev/null
fi
echo "=== parity_field_dsl: flowc = ${BIN} ==="

# Fixture corpus: the fixtures plus the one example that uses the DSL.
fixtures=()
for f in "$FIX"/*.flow; do
    fixtures+=("$f")
done
fixtures+=(examples/evolution/heat_diffusion.flow)

golden_base() {
    local f="$1"
    printf '%s/%s\n' "$FIX" "$(basename "$f" .flow)"
}

# flowc_expand <in> <out.flow> <out.err>: expanded source, or the message.
flowc_expand() {
    local in="$1" out="$2" err="$3"
    rm -f "$out" "$err"
    local log
    set +e
    log="$(FLOWC_EXPAND_ONLY=1 FLOWC_IN="$in" FLOWC_OUT="$out" "$BIN" 2>&1)"
    local code=$?
    set -e
    if [[ "$code" -ne 0 ]]; then
        rm -f "$out"
        printf '%s\n' "$log" | sed -n 's/^flowc field: //p' > "$err"
        if [[ ! -s "$err" ]]; then
            printf 'flowc failed without a field diagnostic: %s\n' "$log" > "$err"
        fi
    fi
}

# python_expand <rev> <list-file> <outdir>: run the Python reference at <rev>.
python_expand() {
    local r="$1" list="$2" outdir="$3"
    mkdir -p "$WORK/pyref/flow"
    git show "${r}:src/flow/field_dsl.py" > "$WORK/pyref/flow/field_dsl_ref.py"
    python3 - "$WORK/pyref/flow" "$list" "$outdir" <<'PY'
import importlib.util, os, sys
ref_path = os.path.join(sys.argv[1], "field_dsl_ref.py")
spec = importlib.util.spec_from_file_location("field_dsl_ref", ref_path)
mod = importlib.util.module_from_spec(spec)
sys.modules["field_dsl_ref"] = mod
spec.loader.exec_module(mod)
outdir = sys.argv[3]
for path in open(sys.argv[2]).read().split("\n"):
    if not path:
        continue
    key = path.replace("/", "__")
    with open(path, encoding="utf-8", newline="") as f:
        text = f.read()
    try:
        out = mod.expand_field_dsl(text)
    except SyntaxError as e:
        with open(os.path.join(outdir, key + ".err"), "w", encoding="utf-8") as f:
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

# 2. Every other .flow in the repo: no DSL, so flowc must leave it untouched.
find examples tests lib -name '*.flow' -type f | LC_ALL=C sort > "$WORK/corpus.txt"
corpus_n=0
corpus_fail=0
while IFS= read -r f; do
    [[ "$f" == examples/evolution/heat_diffusion.flow ]] && continue
    key="${f//\//__}"
    corpus_n=$((corpus_n + 1))
    flowc_expand "$f" "$WORK/flowc/$key.flow" "$WORK/flowc/$key.err"
    if [[ ! -f "$WORK/flowc/$key.flow" ]] || ! cmp -s "$f" "$WORK/flowc/$key.flow"; then
        corpus_fail=$((corpus_fail + 1))
        echo "FAIL passthrough $f" >&2
    fi
done < "$WORK/corpus.txt"
echo "passthrough: files=${corpus_n} fail=${corpus_fail}"
fail=$((fail + corpus_fail))

# 3. Optional: live diff against the Python reference at <rev>.
if [[ "$mode" == "--python" ]]; then
    [[ -n "$rev" ]] || { echo "usage: $0 --python <rev>" >&2; exit 2; }
    { printf '%s\n' "${fixtures[@]}"; cat "$WORK/corpus.txt"; } > "$WORK/all.txt"
    python_expand "$rev" "$WORK/all.txt" "$WORK/python"
    live_n=0
    live_fail=0
    while IFS= read -r f; do
        [[ -n "$f" ]] || continue
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
fi

# 4. End to end: the DSL example compiles on flowc alone and runs clean.
FLOWC_BUNDLE=1 FLOWC_DIR=examples/evolution \
FLOWC_IN=examples/evolution/heat_diffusion.flow FLOWC_OUT="$WORK/heat.c" \
    "$BIN" >"$WORK/heat_emit.log" 2>&1 || true
if [[ -s "$WORK/heat.c" ]] && "${CC:-cc}" -O1 -o "$WORK/heat" "$WORK/heat.c" -lm 2>"$WORK/heat_cc.log"; then
    set +e
    "$WORK/heat" > "$WORK/heat_run.log"
    code=$?
    set -e
    if [[ "$code" -eq 0 ]] && grep -Fq 'OK: field T / boundary / T_field_step' "$WORK/heat_run.log"; then
        echo "e2e: heat_diffusion exit 0 on flowc"
    else
        fail=$((fail + 1))
        echo "FAIL e2e: heat_diffusion exit ${code}" >&2
        tail -5 "$WORK/heat_run.log" >&2
    fi
else
    fail=$((fail + 1))
    echo "FAIL e2e: heat_diffusion did not build on flowc" >&2
    cat "$WORK/heat_emit.log" "$WORK/heat_cc.log" 2>/dev/null | head -20 >&2
fi

if [[ "$fail" -ne 0 ]]; then
    echo "parity_field_dsl: FAIL (${fail})"
    exit 1
fi
echo "parity_field_dsl: PASS"
