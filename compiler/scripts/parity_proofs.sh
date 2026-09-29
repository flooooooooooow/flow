#!/usr/bin/env bash
# Parity gate for the proof layer on flowc (#996).
#
# flowc erases `theorem`, `assume`, `therefore` and claim references the way
# the Python host did, and compiler/src/proof_doc.flow replaces the Python
# proof tools (proof_document, geometry_diagram, geometry_script, know,
# proof_kernel and their helpers). This gate holds flowc to that behaviour
# on every examples/verify file.
#
#   ./compiler/scripts/parity_proofs.sh
#       flowc alone: accept/reject matches compiler/parity_proofs/
#       python_rejects.txt, programs with a main() print what
#       compiler/parity_proofs/run/*.expected records, and the proof documents
#       flowc writes are compared with the checked-in ones (reported).
#
#   ./compiler/scripts/parity_proofs.sh --python <rev>
#       also run the Python host from git revision <rev> and require the
#       same accept/reject, the same first diagnostic (line, or the
#       offending token when Python gives no line), the same program
#       output, and byte-identical proof artifacts: .proof.md, .proof.tex,
#       figures, directory mode, the three proof-book bundles, kernels and
#       `flow know`. Needs python3 and git.
#
# The Python proof tools were deleted after 9103c996 (the last revision
# with the prose that has no dashes, which the Flow port follows).
#
# Env: FLOWC_BIN=<path> tests that binary instead of building
# compiler/build/flowc_bootstrap from the checked-in bootstrap C.
# JOBS=<n> parallel emits (default 8).
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
cd "$ROOT"

mode="${1:-}"
rev="${2:-}"
if [[ "$mode" == "--python" && -z "$rev" ]]; then
    echo "usage: $0 [--python <rev>]" >&2
    exit 2
fi
DATA=compiler/parity_proofs
WORK="$ROOT/compiler/build/parity_proofs"
JOBS="${JOBS:-8}"
rm -rf "$WORK"
mkdir -p "$WORK/fc" "$WORK/py" "$WORK/run"

if [[ -n "${FLOWC_BIN:-}" ]]; then
    BIN="$FLOWC_BIN"
else
    BIN="$ROOT/compiler/build/flowc_bootstrap"
    "${CC:-cc}" -O2 -w -o "$BIN" compiler/bootstrap/flowc_stage_a.c -lm
fi
echo "=== parity_proofs: flowc = ${BIN} ==="

git ls-files 'examples/verify/*.flow' | LC_ALL=C sort > "$WORK/files.txt"
total=$(wc -l < "$WORK/files.txt" | tr -d ' ')

# 1. Emit every file on flowc the way flow-driver does (bundle mode when
#    the file imports), keeping the exit code and log.
cat > "$WORK/emit_one.sh" <<'SH'
#!/usr/bin/env bash
f="$1"; key="${f//\//__}"; out="$WORK/fc"
if grep -Eq '^[[:space:]]*import[[:space:]]' "$f"; then
    FLOWC_BUNDLE=1 FLOWC_DIR="$ROOT" FLOWC_TYPECHECK=1 FLOWC_IN="$ROOT/$f" \
        FLOWC_OUT="$out/$key.c" "$BIN" > "$out/$key.log" 2>&1
else
    FLOWC_TYPECHECK=1 FLOWC_IN="$f" FLOWC_OUT="$out/$key.c" "$BIN" > "$out/$key.log" 2>&1
fi
echo $? > "$out/$key.rc"
SH
chmod +x "$WORK/emit_one.sh"
export ROOT WORK BIN
xargs -P "$JOBS" -n 1 "$WORK/emit_one.sh" < "$WORK/files.txt"

fail=0
fc_ok=0
grep -v '^#' "$DATA/python_rejects.txt" | LC_ALL=C sort > "$WORK/rejects.txt"
reject_bad=0
while IFS= read -r f; do
    key="${f//\//__}"
    rc=$(cat "$WORK/fc/$key.rc")
    if [[ "$rc" == 0 ]]; then fc_ok=$((fc_ok + 1)); fi
    if grep -Fxq "$f" "$WORK/rejects.txt"; then
        want=1
    else
        want=0
    fi
    got=0
    [[ "$rc" != 0 ]] && got=1
    if [[ "$want" != "$got" ]]; then
        reject_bad=$((reject_bad + 1))
        echo "FAIL accept/reject $f: flowc rc=$rc" >&2
    fi
done < "$WORK/files.txt"
echo "emit: flowc accepts ${fc_ok}/${total}; accept/reject mismatches vs recorded list: ${reject_bad}"
fail=$((fail + reject_bad))

# 2. Programs with a main(): build the flowc C, run it, compare output.
run_bad=0
run_n=0
for exp in "$DATA"/run/*.expected; do
    key="$(basename "$exp" .expected)"
    run_n=$((run_n + 1))
    if "${CC:-cc}" -w -O1 -o "$WORK/run/$key" "$WORK/fc/$key.c" -lm 2>"$WORK/run/$key.cc" \
        && "$WORK/run/$key" > "$WORK/run/$key.out" 2>&1 \
        && cmp -s "$exp" "$WORK/run/$key.out"; then
        :
    else
        run_bad=$((run_bad + 1))
        echo "FAIL run ${key}" >&2
    fi
done
echo "run: ${run_n} program(s), mismatches: ${run_bad}"
fail=$((fail + run_bad))

# 3. Proof documents for every file, mirrored under $WORK/docs_fc.
FLOWC_PROOF_DOC=1 FLOWC_PROOF_ROOT="$ROOT" FLOWC_PROOF_LIST="$WORK/files.txt" \
    FLOWC_PROOF_OUT="$WORK/docs_fc" FLOWC_PROOF_MIRROR=1 FLOWC_PROOF_QUIET=1 "$BIN"
docs_same=0
docs_n=0
while IFS= read -r f; do
    d="$(dirname "$f")"; s="$(basename "$f" .flow)"
    for ext in proof.md proof.tex; do
        docs_n=$((docs_n + 1))
        if cmp -s "$WORK/docs_fc/$d/$s.$ext" "$d/$s.$ext"; then docs_same=$((docs_same + 1)); fi
    done
done < "$WORK/files.txt"
echo "docs: ${docs_same}/${docs_n} match the checked-in .proof.md/.proof.tex (report only)"

if [[ "$mode" != "--python" ]]; then
    if [[ "$fail" -ne 0 ]]; then
        echo "parity_proofs: FAIL (${fail})"
        exit 1
    fi
    echo "parity_proofs: PASS"
    exit 0
fi

# ── Live comparison with the Python host at <rev> ─────────────────────
REF="$WORK/pyref"
mkdir -p "$REF"
git archive "$rev" src/flow tools/doc | tar -x -C "$REF"
# The Python tools find the verify corpus relative to their own tree.
ln -s "$ROOT/lib" "$REF/lib"
ln -s "$ROOT/examples" "$REF/examples"
export REF

# 4. Python transpiler on every file.
cat > "$WORK/py_one.sh" <<'SH'
#!/usr/bin/env bash
f="$1"; key="${f//\//__}"; out="$WORK/py"
PYTHONPATH="$REF/src" python3 -m flow.transpiler "$f" --c --lenient -o "$out/$key.c" > "$out/$key.log" 2>&1
echo $? > "$out/$key.rc"
SH
chmod +x "$WORK/py_one.sh"
xargs -P "$JOBS" -n 1 "$WORK/py_one.sh" < "$WORK/files.txt"

# Python's token names for the flowc token text in "unexpected token".
py_token() {
    case "$1" in
        COLON) echo ":" ;;
        EQUALS) echo "==" ;;
        ASSIGN) echo "=" ;;
        PLUS) echo "+" ;;
        MINUS) echo "-" ;;
        RPAREN) echo ")" ;;
        LPAREN) echo "(" ;;
        RBRACE) echo "}" ;;
        LBRACE) echo "{" ;;
        COMMA) echo "," ;;
        *) echo "?$1" ;;
    esac
}

live_bad=0
py_ok=0
diag_line=0
diag_token=0
diag_bad=0
while IFS= read -r f; do
    key="${f//\//__}"
    prc=$(cat "$WORK/py/$key.rc")
    frc=$(cat "$WORK/fc/$key.rc")
    [[ "$prc" == 0 ]] && py_ok=$((py_ok + 1))
    pa=0; fa=0
    [[ "$prc" == 0 ]] && pa=1
    [[ "$frc" == 0 ]] && fa=1
    if [[ "$pa" != "$fa" ]]; then
        live_bad=$((live_bad + 1))
        echo "FAIL live accept/reject $f: python rc=$prc flowc rc=$frc" >&2
        continue
    fi
    if [[ "$prc" != 0 ]]; then
        pl=$(grep -m1 -oE 'at line [0-9]+' "$WORK/py/$key.log" | grep -oE '[0-9]+' || true)
        fl=$(grep -m1 -oE '\.flow:[0-9]+:[0-9]+:' "$WORK/fc/$key.log" | cut -d: -f2 || true)
        if [[ -n "$pl" ]]; then
            if [[ "$pl" == "$fl" ]]; then
                diag_line=$((diag_line + 1))
            else
                diag_bad=$((diag_bad + 1))
                echo "FAIL diagnostic line $f: python $pl, flowc $fl" >&2
            fi
        else
            ptok=$(grep -m1 -oE 'Unexpected token in expression: TokenType\.[A-Z_]+' "$WORK/py/$key.log" | sed 's/.*TokenType\.//' || true)
            ftok=$(grep -m1 -oE "unexpected token '[^']*'" "$WORK/fc/$key.log" | sed "s/unexpected token '//; s/'\$//" || true)
            if [[ -n "$ptok" && "$(py_token "$ptok")" == "$ftok" ]]; then
                diag_token=$((diag_token + 1))
            else
                diag_bad=$((diag_bad + 1))
                echo "FAIL diagnostic token $f: python $ptok, flowc $ftok" >&2
            fi
        fi
    fi
done < "$WORK/files.txt"
echo "live python@${rev}: python accepts ${py_ok}/${total}, flowc ${fc_ok}/${total}; accept/reject mismatches: ${live_bad}"
echo "live diagnostics: same line ${diag_line}, same token ${diag_token}, mismatches ${diag_bad}"
fail=$((fail + live_bad + diag_bad))

# 5. Program output: the Python C against flowc's, for every program.
prog_n=0
prog_bad=0
while IFS= read -r f; do
    key="${f//\//__}"
    [[ "$(cat "$WORK/py/$key.rc")" == 0 ]] || continue
    grep -Eq '^[[:space:]]*(export[[:space:]]+)?function[[:space:]]+main[[:space:]]*\(' "$f" || continue
    prog_n=$((prog_n + 1))
    "${CC:-cc}" -w -O1 -o "$WORK/run/$key.py" "$WORK/py/$key.c" -lm 2>/dev/null || true
    "${CC:-cc}" -w -O1 -o "$WORK/run/$key.fc" "$WORK/fc/$key.c" -lm 2>/dev/null || true
    set +e
    "$WORK/run/$key.py" > "$WORK/run/$key.py.out" 2>&1; pe=$?
    "$WORK/run/$key.fc" > "$WORK/run/$key.fc.out" 2>&1; fe=$?
    set -e
    if [[ "$pe" != "$fe" ]] || ! cmp -s "$WORK/run/$key.py.out" "$WORK/run/$key.fc.out"; then
        prog_bad=$((prog_bad + 1))
        echo "FAIL program output $f (exit python $pe, flowc $fe)" >&2
    fi
done < "$WORK/files.txt"
echo "live programs: ${prog_n} run on both hosts, mismatches: ${prog_bad}"
fail=$((fail + prog_bad))

# 6. Proof artifacts from the Python tools at <rev>.
git ls-files 'lib/verify/*.flow' | LC_ALL=C sort > "$WORK/lib_files.txt"
cat "$WORK/files.txt" "$WORK/lib_files.txt" > "$WORK/doc_files.txt"
rm -rf "$WORK/docs_fc"
FLOWC_PROOF_DOC=1 FLOWC_PROOF_ROOT="$ROOT" FLOWC_PROOF_LIST="$WORK/doc_files.txt" \
    FLOWC_PROOF_OUT="$WORK/docs_fc" FLOWC_PROOF_MIRROR=1 FLOWC_PROOF_QUIET=1 "$BIN"

# Directory mode (write_proof_artifacts_tree) on copies of two directories.
for d in geometry euclid/book-ii; do
    mkdir -p "$WORK/tree_py/$d" "$WORK/tree_fc/$d"
    cp examples/verify/"$d"/*.flow "$WORK/tree_py/$d/"
    cp examples/verify/"$d"/*.flow "$WORK/tree_fc/$d/"
    mkdir -p "$WORK/tree_py/$d/scripts" "$WORK/tree_fc/$d/scripts"
    if [[ -d examples/verify/$d/scripts ]]; then
        cp examples/verify/"$d"/scripts/* "$WORK/tree_py/$d/scripts/"
        cp examples/verify/"$d"/scripts/* "$WORK/tree_fc/$d/scripts/"
    fi
    (cd "$WORK/tree_fc" && find "$d" -maxdepth 1 -name '*.flow' -type f | tr '/' '\001' \
        | LC_ALL=C sort | tr '\001' '/' > "$WORK/tree_list.txt" \
        && FLOWC_PROOF_DOC=1 FLOWC_PROOF_ROOT="$ROOT" FLOWC_PROOF_LIST="$WORK/tree_list.txt" \
            FLOWC_PROOF_TREE=1 "$BIN" > "$WORK/tree_fc_$(echo "$d" | tr / _).log")
done

# Kernel cases: file, then NAME=VALUE pairs.
cat > "$WORK/kernel_cases.txt" <<'EOF'
lib/verify/Nat.flow
lib/verify/Nat.flow|n=0
lib/verify/Nat.flow|n=3|m=0
lib/verify/Bool.flow|a=true
lib/verify/Bool.flow|a=false|b=yes
examples/verify/math/derived/Bool-and-assoc.flow|a=false
examples/verify/math/derived/Bool-de-morgan.flow|a=false
examples/verify/math/derived/Nat-plus-commutes.flow|a=0|b=1
examples/verify/geometry/taylor-sin-maclaurin.flow
examples/verify/math/Int-square-nonneg.flow|n=2
examples/verify/circuits/full_adder.flow|A=1
EOF
mkdir -p "$WORK/kernel"
i=0
while IFS= read -r line; do
    kf="${line%%|*}"
    params=""
    [[ "$kf" != "$line" ]] && params="$(printf '%s' "${line#*|}" | tr '|' '\n')"
    FLOWC_PROOF_DOC=1 FLOWC_PROOF_ROOT="$ROOT" FLOWC_PROOF_KERNEL=1 FLOWC_IN="$kf" \
        FLOWC_KERNEL_OUT="$WORK/kernel/fc$i.json" FLOWC_KERNEL_PARAMS="$params" \
        FLOWC_KERNEL_PLOT="$WORK/kernel/fc$i.dot" "$BIN" > /dev/null
    i=$((i + 1))
done < "$WORK/kernel_cases.txt"

# Bundles and `flow know`.
for b in book basic geometry; do
    FLOWC_PROOF_DOC=1 FLOWC_PROOF_ROOT="$ROOT" FLOWC_PROOF_BOOK="$b" \
        FLOWC_PROOF_OUT="$WORK/book_fc" FLOWC_PROOF_NO_REFRESH=1 "$BIN" > /dev/null
done
cat > "$WORK/know_queries.txt" <<'EOF'
Nat/+.zero-right
verify.Nat/+.zero-right
Bool/||.commutes
Eq/=.reflexive
«Nat» «addition» «order does not matter»
Nat.addition.zero_is_the_left_identity
examples.verify.math.derived.«Nat» «addition» «zero is the right identity»
zero is the left identity
FullAdder/out.correct
«Geometry» «triangle» «interior angles sum to two right angles»
Nope/x.missing
right identity
lib.verify.Nat/+.zero-left
EOF
mkdir -p "$WORK/know_fc"
: > "$WORK/know_fc/know.txt"
while IFS= read -r q; do
    if ! FLOWC_PROOF_DOC=1 FLOWC_PROOF_ROOT="$ROOT" FLOWC_KNOW="$q" "$BIN" >> "$WORK/know_fc/know.txt" 2>/dev/null; then
        echo "UNKNOWN $q" >> "$WORK/know_fc/know.txt"
    fi
done < "$WORK/know_queries.txt"
set +e
FLOWC_PROOF_DOC=1 FLOWC_PROOF_ROOT="$ROOT" FLOWC_KNOW_LINT=1 "$BIN" > "$WORK/know_fc/lint.txt"
set -e

# The same with the Python tools.
python3 - "$REF" "$ROOT" "$WORK" <<'PY'
import os, subprocess, sys
from pathlib import Path
ref, root, work = sys.argv[1], sys.argv[2], sys.argv[3]
sys.path.insert(0, os.path.join(ref, "src"))
os.chdir(root)
import flow.know as know
import flow.proof_document as pdoc
from flow.claim_path import check_duplicate_claims
from flow.proof_kernel import compile_file_kernel, write_kernel_json, _plot_dot

for f in open(os.path.join(work, "doc_files.txt")).read().split("\n"):
    if f:
        pdoc.write_proof_artifacts(f, output_dir=os.path.join(work, "docs_py", os.path.dirname(f)))

for d in ("geometry", "euclid/book-ii"):
    here = os.getcwd()
    os.chdir(os.path.join(work, "tree_py"))
    pdoc.write_proof_artifacts_tree(d, recursive=False)
    os.chdir(here)

out = os.path.join(work, "kernel")
cases = [l.split("|") for l in open(os.path.join(work, "kernel_cases.txt")).read().split("\n") if l]
for i, parts in enumerate(cases):
    inst = {}
    for pair in parts[1:]:
        k, v = pair.split("=", 1)
        inst[k.strip()] = v.strip()
    write_kernel_json(parts[0], output=os.path.join(out, "py%d.json" % i), instantiation=inst or None)
    _plot_dot(compile_file_kernel(parts[0], instantiation=inst or None), os.path.join(out, "py%d.dot" % i), title=None)

book = os.path.join(work, "book_py")
os.makedirs(book, exist_ok=True)
with open(os.path.join(book, "flow-proof-book.tex"), "w", encoding="utf-8") as fh:
    fh.write(pdoc.render_side_by_side_bundle(book_parts=pdoc.load_proof_book(root), title="Flow Proof Book"))
with open(os.path.join(book, "basic-proofs-side-by-side.tex"), "w", encoding="utf-8") as fh:
    fh.write(pdoc.render_side_by_side_bundle(pdoc.load_basic_proof_bundle(root), title="Flow Basic Proofs"))
with open(os.path.join(book, "geometry-proofs-side-by-side.tex"), "w", encoding="utf-8") as fh:
    fh.write(pdoc.render_side_by_side_bundle(pdoc.load_geometry_proof_bundle(root), title="Flow Euclidean Geometry"))

kdir = os.path.join(work, "know_py")
os.makedirs(kdir, exist_ok=True)
with open(os.path.join(kdir, "know.txt"), "w", encoding="utf-8") as fh:
    for q in open(os.path.join(work, "know_queries.txt"), encoding="utf-8").read().split("\n"):
        if not q:
            continue
        e = know.lookup_claim(q, root)
        fh.write(("UNKNOWN " + q) if e is None else know.format_know(e))
        fh.write("\n")
# The Python lint walks rglob unsorted; compare in sorted path order.
rows = []
for r in know._default_search_roots(root):
    for fp in sorted(Path(r).rglob("*.flow"), key=lambda p: str(p).replace("/", "\x01")):
        doc = pdoc.parse_proof_file(str(fp))
        for thm in doc.theorems:
            expr = thm.claim_expr or ""
            if not expr:
                for step in thm.steps:
                    if step.kind == "therefore":
                        expr = step.text
                        break
            if expr:
                rows.append((thm.claim_path, expr, str(fp)))
errs = check_duplicate_claims(rows)
with open(os.path.join(kdir, "lint.txt"), "w", encoding="utf-8") as fh:
    fh.write("".join(e + "\n" for e in errs) if errs else "No duplicate claims found.\n")
PY

# Compare two trees file by file; prints "same/total" and fails on any gap.
compare_trees() {
    local label="$1" a="$2" b="$3"
    local n=0 same=0 bad=0 f
    while IFS= read -r f; do
        n=$((n + 1))
        if [[ -f "$b/$f" ]] && cmp -s "$a/$f" "$b/$f"; then
            same=$((same + 1))
        else
            bad=$((bad + 1))
            echo "FAIL ${label}: $f differs" >&2
        fi
    done < <(cd "$a" && find . -type f ! -name '*.flow' ! -path './*/scripts/*' | LC_ALL=C sort)
    local nb
    nb=$(cd "$b" && find . -type f ! -name '*.flow' ! -path './*/scripts/*' | wc -l | tr -d ' ')
    if [[ "$nb" != "$n" ]]; then
        bad=$((bad + 1))
        echo "FAIL ${label}: python wrote ${n} files, flowc ${nb}" >&2
    fi
    echo "live ${label}: ${same}/${n} files byte-identical"
    fail=$((fail + bad))
}
compare_trees "proof documents" "$WORK/docs_py" "$WORK/docs_fc"
compare_trees "directory mode" "$WORK/tree_py" "$WORK/tree_fc"
compare_trees "bundles" "$WORK/book_py" "$WORK/book_fc"
k_n=0
k_bad=0
for j in "$WORK"/kernel/py*.json "$WORK"/kernel/py*.dot; do
    k_n=$((k_n + 1))
    fcf="$WORK/kernel/fc${j##*/py}"
    if ! cmp -s "$j" "$fcf"; then
        k_bad=$((k_bad + 1))
        echo "FAIL kernel ${j##*/}" >&2
    fi
done
echo "live kernels: $((k_n - k_bad))/${k_n} files byte-identical"
fail=$((fail + k_bad))
compare_trees "flow know" "$WORK/know_py" "$WORK/know_fc"

if [[ "$fail" -ne 0 ]]; then
    echo "parity_proofs: FAIL (${fail})"
    exit 1
fi
echo "parity_proofs: PASS"
