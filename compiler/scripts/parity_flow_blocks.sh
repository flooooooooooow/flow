#!/usr/bin/env bash
# Parity gate for flow-block lowering (compiler/src/flow_blocks.flow).
#
# The Flow port replaced src/flow/flow_blocks.py, which lowered a parsed
# FlowDecl to AST. flowc lowers the same block to Flow source before parse,
# so parity is checked on the parsed result: the Python parser from a git
# revision lowers the original source, parses flowc's expansion, and the
# two declaration lists must be equal (locations and `has_self` aside; the
# latter only gates tail-call rewriting, and flow functions never call
# themselves). Diagnostics must match the Python text: message, line,
# column and hint.
#
# Goldens beside each fixture in compiler/fixtures/flow_blocks/:
#   ok_*.flow   -> .expected  flowc's expansion, recorded after the tree
#                             check against Python passed
#   err_*.flow  -> .error     the Python message (first line) and hint
#   run_*.flow  -> .out       stdout, exit code and stderr of the program
#                             built by the Python host
#
#   ./compiler/scripts/parity_flow_blocks.sh
#       flowc vs goldens, the run fixtures and tests/lang flow tests on
#       flowc, passthrough of every tracked .flow without a flow block,
#       then one example end to end with python stubbed out on PATH.
#
#   ./compiler/scripts/parity_flow_blocks.sh --python <rev>
#       also the tree check against the Python at <rev> over the fixtures
#       and every tracked .flow. Needs python3 and git.
#
#   ./compiler/scripts/parity_flow_blocks.sh --write-golden <rev>
#       re-record the goldens from the Python at <rev>.
#
# The last Python revision is 7527ab37.
#
# Env: FLOWC_BIN=<path> tests that binary instead of building
# compiler/build/flowc_bootstrap from the checked-in bootstrap C.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
cd "$ROOT"

FIX=compiler/fixtures/flow_blocks
WORK=compiler/build/parity_flow_blocks
mode="${1:-}"
rev="${2:-}"
rm -rf "$WORK"
mkdir -p "$WORK/flowc" "$WORK/run"

if [[ -n "${FLOWC_BIN:-}" ]]; then
    BIN="$FLOWC_BIN"
else
    BIN=compiler/build/flowc_bootstrap
    "${CC:-cc}" -O2 -o "$BIN" compiler/bootstrap/flowc_stage_a.c 2>/dev/null
fi
echo "=== parity_flow_blocks: flowc = ${BIN} ==="

expand_fixtures=()
run_fixtures=()
for f in "$FIX"/*.flow; do
    case "$(basename "$f")" in
        run_*) run_fixtures+=("$f") ;;
        *) expand_fixtures+=("$f") ;;
    esac
done

golden_base() {
    printf '%s/%s\n' "$FIX" "$(basename "$1" .flow)"
}

# flowc_expand <in> <out.flow> <out.err> [stages]: flow-block expansion of
# <in> (or the given FLOWC_EXPAND_ONLY stages), or the diagnostic
# ("message" then the hint on a second line).
flowc_expand() {
    local in="$1" out="$2" err="$3" stages="${4:-flow}"
    rm -f "$out" "$err"
    local log code
    set +e
    log="$(FLOWC_EXPAND_ONLY="$stages" FLOWC_IN="$in" FLOWC_OUT="$out" "$BIN" 2>&1)"
    code=$?
    set -e
    if [[ "$code" -ne 0 ]]; then
        rm -f "$out"
        {
            printf '%s\n' "$log" | sed -n 's/^flowc flow: //p'
            printf '%s\n' "$log" | sed -n 's/^flowc flow hint: //p'
        } > "$err"
        if [[ ! -s "$err" ]]; then
            printf '%s\n' "$log" > "$err"
        fi
    fi
}

# run_program <src> <out>: build <src> on flowc, run it, record stdout,
# the exit code and stderr.
run_program() {
    local src="$1" out="$2" key
    key="$(basename "$out")"
    rm -f "$out" "$WORK/run/$key.c" "$WORK/run/$key.bin"
    FLOWC_BUNDLE=1 FLOWC_DIR=. FLOWC_IN="$src" FLOWC_OUT="$WORK/run/$key.c" \
        "$BIN" > "$WORK/run/$key.emit" 2>&1 || true
    if [[ ! -s "$WORK/run/$key.c" ]]; then
        grep -v '^bundle_' "$WORK/run/$key.emit" | head -5 > "$out"
        echo "build failed" >> "$out"
        return
    fi
    if ! "${CC:-cc}" -O1 -w -o "$WORK/run/$key.bin" "$WORK/run/$key.c" -lm 2> "$WORK/run/$key.cc"; then
        head -5 "$WORK/run/$key.cc" > "$out"
        echo "cc failed" >> "$out"
        return
    fi
    local code
    set +e
    "$WORK/run/$key.bin" > "$out" 2> "$WORK/run/$key.stderr" < /dev/null
    code=$?
    set -e
    echo "exit=$code" >> "$out"
    cat "$WORK/run/$key.stderr" >> "$out"
}

# tree_check <rev> <list> <report>: the Python at <rev> against flowc, per
# file. Writes "OK <path>", "ERR <path> <text>", "SKIP <path>" or
# "FAIL <path> <why>" lines.
tree_check() {
    local r="$1" list="$2" report="$3"
    rm -rf "$WORK/pyref"
    mkdir -p "$WORK/pyref"
    git archive "$r" src/flow | tar -x -C "$WORK/pyref"
    python3 - "$WORK/pyref/src" "$BIN" "$list" "$report" <<'PY'
import os, subprocess, sys, tempfile

ref_src, flowc, listfile, report = sys.argv[1:5]
sys.path.insert(0, ref_src)
from flow import parser as P  # noqa: E402

# Positions and metadata. The comparison covers the lowered program only.
SKIP = {
    "location", "line", "column", "end_line", "end_column", "is_exported",
    "flow_decl", "recognition_manifest", "op_line", "captures", "text",
    "has_self",
}


def lit(v):
    s = str(v)
    try:
        if any(ch in s for ch in ".eE") and not s.startswith("0x"):
            return repr(float(s))
        return str(int(s, 0))
    except ValueError:
        return s


def norm(o):
    if isinstance(o, (list, tuple)):
        return [norm(x) for x in o]
    if o is None or isinstance(o, (str, int, float, bool)):
        # Name_new's local: `self` is a keyword in source, so the
        # expansion spells it `__self`.
        return "self" if o == "__self" else o
    cls = type(o).__name__
    if cls == "Type":
        el = getattr(o, "element_type", None)
        return ("T", o.name, bool(getattr(o, "is_pointer", False)),
                el.name if el is not None else None)
    if cls == "Literal":
        return ("Literal", lit(o.value))
    if cls == "ExpressionStatement":
        return norm(o.expression)
    if not hasattr(o, "__dict__"):
        return repr(o)
    d = {}
    for k, v in vars(o).items():
        if k in SKIP or k.startswith("_"):
            continue
        d[k] = norm(v)
    return (cls, sorted(d.items()))


def diag(e):
    lines = str(e).split("\n")
    out = lines[0]
    for ln in lines:
        if ln.strip().startswith("Hint: "):
            out += "\n" + ln.strip()[len("Hint: "):]
            break
    return out


def run(env_extra, path):
    env = dict(os.environ, FLOWC_IN=path, **env_extra)
    env.pop("FLOWC_BUNDLE", None)
    return subprocess.run([flowc], env=env, capture_output=True)


rep = open(report, "w", encoding="utf-8")
for path in open(listfile).read().split("\n"):
    if not path:
        continue
    with tempfile.TemporaryDirectory() as td:
        # Field and dynamics DSLs expand first, on flowc (each has its own
        # gate), so both sides start from the same source.
        pre_path = os.path.join(td, "pre.flow")
        pre = run({"FLOWC_EXPAND_ONLY": "field,dynamics", "FLOWC_OUT": pre_path}, path)
        if pre.returncode != 0:
            rep.write(f"SKIP {path}\n")
            continue
        code = open(pre_path, encoding="utf-8", newline="").read()
        out_path = os.path.join(td, "out.flow")
        fc = run({"FLOWC_EXPAND_ONLY": "flow", "FLOWC_OUT": out_path}, pre_path)
        fc_err = None
        text = None
        if fc.returncode != 0:
            so = fc.stdout.decode("utf-8", "replace").splitlines()
            msg = [ln[len("flowc flow: "):] for ln in so if ln.startswith("flowc flow: ")]
            hint = [ln[len("flowc flow hint: "):] for ln in so if ln.startswith("flowc flow hint: ")]
            fc_err = (msg[0] if msg else "flowc failed") + ("\n" + hint[0] if hint else "")
        else:
            text = open(out_path, encoding="utf-8", newline="").read()
    py_err = None
    try:
        py = P.Parser(P.Lexer(code)).parse()
    except Exception as e:  # noqa: BLE001
        py_err = diag(e)
    if py_err is not None:
        if fc_err == py_err:
            rep.write(f"ERR {path} {py_err!r}\n")
            continue
        if fc_err is None:
            # Python fails outside the flow blocks: flowc's expansion must
            # fail the same way when Python parses it.
            try:
                P.Parser(P.Lexer(text)).parse(expand_flows=False)
                rep.write(f"FAIL {path} python error {py_err!r}, flowc expanded\n")
            except Exception as e2:  # noqa: BLE001
                a = diag(e2).split(" at line")[0]
                if a == py_err.split(" at line")[0]:
                    rep.write(f"OK {path}\n")
                else:
                    rep.write(f"FAIL {path} python {py_err!r} vs {diag(e2)!r}\n")
            continue
        rep.write(f"FAIL {path} python {py_err!r} flowc {fc_err!r}\n")
        continue
    if fc_err is not None:
        rep.write(f"FAIL {path} flowc error {fc_err!r}, python lowered it\n")
        continue
    try:
        got = P.Parser(P.Lexer(text)).parse(expand_flows=False)
    except Exception as e:  # noqa: BLE001
        rep.write(f"FAIL {path} expansion does not parse: {diag(e)!r}\n")
        continue
    if norm(py) == norm(got):
        rep.write(f"OK {path}\n")
    else:
        rep.write(f"FAIL {path} declaration trees differ\n")
rep.close()
PY
}

if [[ "$mode" == "--write-golden" ]]; then
    [[ -n "$rev" ]] || { echo "usage: $0 --write-golden <rev>" >&2; exit 2; }
    printf '%s\n' "${expand_fixtures[@]}" > "$WORK/fixtures.txt"
    tree_check "$rev" "$WORK/fixtures.txt" "$WORK/tree.txt"
    bad=0
    for f in "${expand_fixtures[@]}"; do
        base="$(golden_base "$f")"
        key="${f//\//__}"
        rm -f "$base.expected" "$base.error"
        line="$(grep -F " $f" "$WORK/tree.txt" | head -1)"
        case "$line" in
            "OK "*)
                flowc_expand "$f" "$WORK/flowc/$key.flow" "$WORK/flowc/$key.err"
                cp "$WORK/flowc/$key.flow" "$base.expected"
                ;;
            "ERR "*)
                flowc_expand "$f" "$WORK/flowc/$key.flow" "$WORK/flowc/$key.err"
                cp "$WORK/flowc/$key.err" "$base.error"
                ;;
            *)
                bad=$((bad + 1))
                echo "not recorded: $line" >&2
                ;;
        esac
    done
    # Run fixtures: the program built by the Python host at <rev>.
    rm -rf "$WORK/pyrev"
    mkdir -p "$WORK/pyrev"
    git archive "$rev" | tar -x -C "$WORK/pyrev"
    for f in "${run_fixtures[@]}"; do
        base="$(golden_base "$f")"
        name="$(basename "$f" .flow)"
        cp "$f" "$WORK/pyrev/$name.flow"
        (cd "$WORK/pyrev" && FLOW_HOST=python ./flow compile "$name.flow" > /dev/null 2>&1) || true
        if [[ ! -x "$WORK/pyrev/build/$name" ]]; then
            bad=$((bad + 1))
            echo "not recorded: $f does not build on the Python host at $rev" >&2
            continue
        fi
        set +e
        "$WORK/pyrev/build/$name" > "$base.out" 2> "$WORK/run/$name.pyerr" < /dev/null
        code=$?
        set -e
        echo "exit=$code" >> "$base.out"
        cat "$WORK/run/$name.pyerr" >> "$base.out"
    done
    echo "wrote goldens from ${rev} (${bad} not recorded)"
    [[ "$bad" -eq 0 ]]
    exit $?
fi

fail=0
pass=0

# 1. Expansion fixtures vs goldens.
for f in "${expand_fixtures[@]}"; do
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

# 2. Programs: the run fixtures against the Python host's output, and the
# tests/lang flow tests, which check themselves and exit 0.
run_pass=0
run_fail=0
for f in "${run_fixtures[@]}"; do
    base="$(golden_base "$f")"
    out="$WORK/run/$(basename "$f" .flow).out"
    run_program "$f" "$out"
    if cmp -s "$base.out" "$out"; then
        run_pass=$((run_pass + 1))
    else
        run_fail=$((run_fail + 1))
        echo "FAIL run $f: output differs from $base.out" >&2
        diff "$base.out" "$out" | head -10 >&2 || true
    fi
done
for f in tests/lang/test_time_blocks.flow tests/lang/test_hybrid_events.flow; do
    out="$WORK/run/$(basename "$f" .flow).out"
    run_program "$f" "$out"
    if grep -qx 'exit=0' "$out"; then
        run_pass=$((run_pass + 1))
    else
        run_fail=$((run_fail + 1))
        echo "FAIL run $f:" >&2
        tail -5 "$out" >&2
    fi
done
echo "programs: pass=${run_pass} fail=${run_fail}"
fail=$((fail + run_fail))

# 3. Every tracked .flow, through every stage (the dynamics DSL strips
# `represent` blocks out of flows first): without a DSL it passes through
# untouched.
git ls-files '*.flow' | grep -v "^${FIX}/" | LC_ALL=C sort > "$WORK/corpus.txt"
same_n=0
flow_n=0
err_n=0
while IFS= read -r f; do
    [[ -f "$f" ]] || continue
    key="${f//\//__}"
    flowc_expand "$f" "$WORK/flowc/$key.flow" "$WORK/flowc/$key.err" all
    if [[ -f "$WORK/flowc/$key.flow" ]] && cmp -s "$f" "$WORK/flowc/$key.flow"; then
        same_n=$((same_n + 1))
    elif [[ -f "$WORK/flowc/$key.flow" ]]; then
        flow_n=$((flow_n + 1))
    else
        err_n=$((err_n + 1))
        echo "$f: $(head -1 "$WORK/flowc/$key.err")" >> "$WORK/corpus_errors.txt"
    fi
done < "$WORK/corpus.txt"
echo "corpus: untouched=${same_n} lowered=${flow_n} diagnosed=${err_n}"

# 4. Optional: the tree check against the Python at <rev>.
if [[ "$mode" == "--python" ]]; then
    [[ -n "$rev" ]] || { echo "usage: $0 --python <rev>" >&2; exit 2; }
    { printf '%s\n' "${expand_fixtures[@]}"; cat "$WORK/corpus.txt"; } > "$WORK/all.txt"
    tree_check "$rev" "$WORK/all.txt" "$WORK/tree.txt"
    live_ok="$(grep -c '^OK ' "$WORK/tree.txt" || true)"
    live_err="$(grep -c '^ERR ' "$WORK/tree.txt" || true)"
    live_skip="$(grep -c '^SKIP ' "$WORK/tree.txt" || true)"
    live_fail="$(grep -c '^FAIL ' "$WORK/tree.txt" || true)"
    grep '^FAIL ' "$WORK/tree.txt" >&2 || true
    echo "live python@${rev}: same trees=${live_ok} same errors=${live_err} skipped=${live_skip} fail=${live_fail}"
    fail=$((fail + live_fail))
elif [[ -s "$WORK/corpus_errors.txt" ]]; then
    # Without Python these cannot be told apart from regressions; the
    # --python run checks each against the Python diagnostic.
    cat "$WORK/corpus_errors.txt"
fi

# 5. End to end: an example with flow blocks, built by `./flow compile` on
# the flowc host with python and python3 stubbed out on PATH.
E2E=examples/evolution/bouncing_ball_evolves.flow
mkdir -p "$WORK/nopy"
printf '#!/bin/sh\necho "python called: $*" >> "%s/nopy/calls.log"\nexit 127\n' "$ROOT/$WORK" > "$WORK/nopy/python3"
cp "$WORK/nopy/python3" "$WORK/nopy/python"
chmod +x "$WORK/nopy/python3" "$WORK/nopy/python"
name="$(basename "$E2E" .flow)"
rm -f "build/$name"
set +e
PATH="$ROOT/$WORK/nopy:$PATH" FLOWC_BIN="$ROOT/$BIN" ./flow compile "$E2E" > "$WORK/e2e_compile.log" 2>&1
PATH="$ROOT/$WORK/nopy:$PATH" "build/$name" > "$WORK/e2e_run.log" 2>&1
code=$?
set -e
if [[ "$code" -eq 0 && ! -s "$WORK/nopy/calls.log" ]]; then
    echo "e2e: ${name} built by ./flow compile on flowc, exit 0, no python call"
else
    fail=$((fail + 1))
    echo "FAIL e2e: ${name} exit ${code}" >&2
    tail -5 "$WORK/e2e_compile.log" "$WORK/e2e_run.log" >&2
    cat "$WORK/nopy/calls.log" 2>/dev/null >&2 || true
fi

if [[ "$fail" -ne 0 ]]; then
    echo "parity_flow_blocks: FAIL (${fail})"
    exit 1
fi
echo "parity_flow_blocks: PASS"
