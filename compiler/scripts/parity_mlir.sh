#!/usr/bin/env bash
# Parity gate for the Flow MLIR emitter (compiler/src/mlirgen.flow).
#
# The emitter replaces the core of src/flow/mlir_generator.py for the
# programs it covers and refuses the rest (see docs/design/mlir-in-flow.md).
# This gate holds it to the Python generator in two ways: the MLIR text, and
# the output of the programs built from it.
#
#   ./compiler/scripts/parity_mlir.sh
#       Golden mode, no Python. Each fixture in compiler/fixtures/mlir/ must
#       emit MLIR equal to its `<name>.mlir` golden after normalization, and
#       every program listed in compiler/fixtures/mlir/corpus.txt must still
#       be accepted and match its recorded digest. When mlir-opt is
#       installed, each fixture is also lowered (compiler/scripts/
#       mlir_lower.sh), linked with clang and run; stdout plus exit code must
#       equal `<name>.out`.
#
#   ./compiler/scripts/parity_mlir.sh --python <rev>
#       Also run the Python generator from git revision <rev> over the
#       fixtures and every .flow under examples/, tests/, lib/, benchmarks/
#       and compiler/fixtures/. Every program flowc accepts must produce the
#       same normalized MLIR as Python. With mlir-opt installed, each such
#       program is built through both MLIR paths (flowc + mlir_lower.sh, and
#       `python -m flow.transpiler --mlir --llvm`) and run; the two runs must
#       agree. Needs python3 and git.
#
#   ./compiler/scripts/parity_mlir.sh --write-golden <rev>
#       Rewrite the fixture goldens and corpus.txt from the Python generator
#       at <rev>. Only programs whose flowc output already equals Python's
#       are recorded in corpus.txt.
#
# Normalization (compiler/scripts/mlir_normalize.awk): SSA values and block
# labels are renamed in order of first appearance and indentation is
# dropped. Python numbers a value before emitting its operands and indents
# unevenly; neither changes the program. Everything else must be equal byte
# for byte, including string globals and their order.
#
# Goldens were recorded from 84806b0d (origin/main after #1020 and #1018;
# the Python MLIR generator is unchanged since eec7463f).
#
# Env: FLOWC_BIN=<path> tests that binary instead of building
# compiler/build/flowc_bootstrap from the checked-in bootstrap C.
# LLVM_PATH / MLIR_OPT / MLIR_TRANSLATE locate the MLIR tools.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
cd "$ROOT"

FIX=compiler/fixtures/mlir
WORK=compiler/build/parity_mlir
NORM=compiler/scripts/mlir_normalize.awk
LOWER=compiler/scripts/mlir_lower.sh
mode="${1:-}"
rev="${2:-}"
case "$mode" in
    ""|--python|--write-golden) ;;
    *) echo "usage: $0 [--python <rev> | --write-golden <rev>]" >&2; exit 2 ;;
esac
if [[ -n "$mode" && -z "$rev" ]]; then
    echo "usage: $0 $mode <rev>" >&2
    exit 2
fi
rm -rf "$WORK"
mkdir -p "$WORK/flowc" "$WORK/python" "$WORK/bin"

if [[ -n "${FLOWC_BIN:-}" ]]; then
    BIN="$FLOWC_BIN"
else
    BIN=compiler/build/flowc_bootstrap
    "${CC:-cc}" -O2 -o "$BIN" compiler/bootstrap/flowc_stage_a.c -lm 2>/dev/null
fi
echo "=== parity_mlir: flowc = ${BIN} ==="

have_mlir=0
if "$LOWER" --tools >/dev/null 2>&1; then
    have_mlir=1
fi

key_of() {
    local f="$1"
    printf '%s\n' "${f//\//__}"
}

# digest <file>: a content hash that needs no Python.
digest() {
    if command -v shasum >/dev/null 2>&1; then
        shasum -a 256 "$1" | cut -d' ' -f1
    else
        sha256sum "$1" | cut -d' ' -f1
    fi
}

# flowc_emit <in.flow> <out.mlir>: 0 when flowc accepts the program.
flowc_emit() {
    local in="$1" out="$2"
    rm -f "$out"
    FLOWC_EMIT=mlir FLOWC_IN="$in" FLOWC_OUT="$out" "$BIN" >"$out.log" 2>&1
}

# flowc_emit_gpu <in.flow> <out.mlir>: the same with @gpu kernels as a
# gpu.module (Python --mlir-gpu).
flowc_emit_gpu() {
    local in="$1" out="$2"
    rm -f "$out"
    FLOWC_MLIR_GPU=1 FLOWC_EMIT=mlir FLOWC_IN="$in" FLOWC_OUT="$out" "$BIN" >"$out.log" 2>&1
}

# run_exe <tag> <src_dir> <out>: run <tag>.exe with no stdin, in a scratch
# directory so programs that write files leave the checkout alone; writes
# stdout, then `exit=<code>`, to <out>. src_dir is kept for the call sites.
run_exe() {
    local tag="$1" src_dir="$2" out="$3"
    local code=0
    mkdir -p "$WORK/rundir"
    set +e
    (cd "$WORK/rundir" && timeout 10 "$ROOT/$tag.exe" </dev/null >"$ROOT/$tag.stdout" 2>/dev/null)
    code=$?
    set -e
    { cat "$tag.stdout"; printf 'exit=%d\n' "$code"; } > "$out"
    rm -f "$tag.stdout"
}

# build_run <tag> <in.mlir or .ll> <kind> <src_dir>: link and run once;
# writes <tag>.out and keeps <tag>.exe. kind is mlir (lower first) or ll.
build_run() {
    local tag="$1" in="$2" kind="$3" src_dir="$4"
    local ll="$tag.ll"
    if [[ "$kind" == "mlir" ]]; then
        if ! "$LOWER" "$in" "$ll" >"$tag.lower.log" 2>&1; then
            return 1
        fi
    else
        ll="$in"
    fi
    if ! timeout 120 "${CC:-clang}" -w -O1 "$ll" -lm -o "$tag.exe" >"$tag.link.log" 2>&1; then
        return 2
    fi
    run_exe "$tag" "$src_dir" "$tag.out"
    return 0
}

# python_setup <rev>: the Python package from git revision <rev>.
PYREF="$WORK/pyref"
python_setup() {
    mkdir -p "$PYREF"
    # The Python host expands flow blocks with flowc built from the
    # bootstrap C of the same revision.
    git archive "$1" src/flow compiler/bootstrap/flowc_stage_a.c | tar -x -C "$PYREF"
    # The resolver's fallback stdlib and packages sit next to src/flow; point
    # them at this checkout's, as flowc (FLOWC_ROOT) uses.
    ln -sfn "$ROOT/lib" "$PYREF/lib"
    ln -sfn "$ROOT/packages" "$PYREF/packages"
}

# python_emit <in.flow> <out.mlir> [--llvm]
python_emit() {
    local in="$1" out="$2"
    shift 2
    PYTHONPATH="$PYREF/src" timeout 120 python3 -m flow.transpiler "$in" --mlir "$@" \
        --lenient -o "$out" >/dev/null 2>"$out.log"
}

fixtures=()
for f in "$FIX"/*.flow; do
    fixtures+=("$f")
done

if [[ "$mode" == "--write-golden" ]]; then
    python_setup "$rev"
    for f in "${fixtures[@]}"; do
        base="$FIX/$(basename "$f" .flow)"
        key="$(key_of "$f")"
        python_emit "$f" "$WORK/python/$key.mlir"
        awk -f "$NORM" "$WORK/python/$key.mlir" > "$base.mlir"
        if [[ "$(basename "$f")" == gpu_* ]]; then
            python_emit "$f" "$WORK/python/$key.gpu.mlir" --mlir-gpu
            awk -f "$NORM" "$WORK/python/$key.gpu.mlir" > "$base.gpu.mlir"
        fi
        if [[ "$have_mlir" -eq 1 ]]; then
            python_emit "$f" "$WORK/python/$key.ll" --llvm
            build_run "$WORK/python/$key" "$WORK/python/$key.ll" ll "$(dirname "$f")"
            cp "$WORK/python/$key.out" "$base.out"
            rm -f "$WORK/python/$key.exe"
        fi
    done
    find examples tests lib benchmarks compiler/fixtures -name '*.flow' -type f \
        | LC_ALL=C sort > "$WORK/all.txt"
    : > "$WORK/corpus.txt"
    n=0
    while IFS= read -r f; do
        [[ "$f" == "$FIX"/* ]] && continue
        key="$(key_of "$f")"
        flowc_emit "$f" "$WORK/flowc/$key.mlir" || continue
        python_emit "$f" "$WORK/python/$key.mlir" || continue
        awk -f "$NORM" "$WORK/flowc/$key.mlir" > "$WORK/flowc/$key.norm"
        awk -f "$NORM" "$WORK/python/$key.mlir" > "$WORK/python/$key.norm"
        if cmp -s "$WORK/flowc/$key.norm" "$WORK/python/$key.norm"; then
            printf '%s %s\n' "$(digest "$WORK/flowc/$key.norm")" "$f" >> "$WORK/corpus.txt"
            n=$((n + 1))
        fi
    done < "$WORK/all.txt"
    {
        echo "# Corpus programs the Flow MLIR emitter covers, with the digest of"
        echo "# their normalized MLIR. Written by parity_mlir.sh --write-golden ${rev}."
        cat "$WORK/corpus.txt"
    } > "$FIX/corpus.txt"
    echo "wrote goldens for ${#fixtures[@]} fixtures and ${n} corpus programs from ${rev}"
    exit 0
fi

fail=0

# 1. Fixtures vs goldens (text); gpu_* fixtures also under FLOWC_MLIR_GPU=1.
fx_pass=0
gpu_pass=0
for f in "${fixtures[@]}"; do
    base="$FIX/$(basename "$f" .flow)"
    key="$(key_of "$f")"
    if ! flowc_emit "$f" "$WORK/flowc/$key.mlir"; then
        fail=$((fail + 1))
        echo "FAIL $f: flowc refused it: $(head -1 "$WORK/flowc/$key.mlir.log")" >&2
        continue
    fi
    awk -f "$NORM" "$WORK/flowc/$key.mlir" > "$WORK/flowc/$key.norm"
    if [[ -f "$base.mlir" ]] && cmp -s "$base.mlir" "$WORK/flowc/$key.norm"; then
        fx_pass=$((fx_pass + 1))
    else
        fail=$((fail + 1))
        echo "FAIL $f: MLIR differs from $base.mlir" >&2
        [[ -f "$base.mlir" ]] && { diff "$base.mlir" "$WORK/flowc/$key.norm" | head -20 >&2 || true; }
    fi
    if [[ "$(basename "$f")" == gpu_* ]]; then
        if flowc_emit_gpu "$f" "$WORK/flowc/$key.gpu.mlir" \
            && awk -f "$NORM" "$WORK/flowc/$key.gpu.mlir" > "$WORK/flowc/$key.gpu.norm" \
            && cmp -s "$base.gpu.mlir" "$WORK/flowc/$key.gpu.norm"; then
            gpu_pass=$((gpu_pass + 1))
        else
            fail=$((fail + 1))
            echo "FAIL $f: GPU-mode MLIR differs from $base.gpu.mlir" >&2
        fi
    fi
done
echo "fixtures (text): pass=${fx_pass} of ${#fixtures[@]}"
echo "fixtures (gpu text): pass=${gpu_pass}"

# 2. Fixtures run (stdout + exit) vs goldens.
if [[ "$have_mlir" -eq 1 ]]; then
    run_pass=0
    for f in "${fixtures[@]}"; do
        base="$FIX/$(basename "$f" .flow)"
        key="$(key_of "$f")"
        [[ -f "$WORK/flowc/$key.mlir" ]] || continue
        if ! build_run "$WORK/flowc/$key" "$WORK/flowc/$key.mlir" mlir "$(dirname "$f")"; then
            fail=$((fail + 1))
            echo "FAIL $f: did not lower or link" >&2
            cat "$WORK/flowc/$key.lower.log" "$WORK/flowc/$key.link.log" 2>/dev/null | head -10 >&2
            continue
        fi
        rm -f "$WORK/flowc/$key.exe"
        if [[ -f "$base.out" ]] && cmp -s "$base.out" "$WORK/flowc/$key.out"; then
            run_pass=$((run_pass + 1))
        else
            fail=$((fail + 1))
            echo "FAIL $f: run output differs from $base.out" >&2
            [[ -f "$base.out" ]] && { diff "$base.out" "$WORK/flowc/$key.out" | head -10 >&2 || true; }
        fi
    done
    echo "fixtures (run): pass=${run_pass} of ${#fixtures[@]}"
else
    echo "fixtures (run): skipped, mlir-opt not found (brew install llvm)"
fi

# 3. Recorded corpus: still accepted, same MLIR.
corpus_n=0
corpus_fail=0
while read -r want f; do
    [[ -z "$want" || "$want" == "#" ]] && continue
    corpus_n=$((corpus_n + 1))
    key="$(key_of "$f")"
    if ! flowc_emit "$f" "$WORK/flowc/$key.mlir"; then
        corpus_fail=$((corpus_fail + 1))
        echo "FAIL corpus $f: no longer accepted: $(head -1 "$WORK/flowc/$key.mlir.log")" >&2
        continue
    fi
    awk -f "$NORM" "$WORK/flowc/$key.mlir" > "$WORK/flowc/$key.norm"
    if [[ "$(digest "$WORK/flowc/$key.norm")" != "$want" ]]; then
        corpus_fail=$((corpus_fail + 1))
        echo "FAIL corpus $f: MLIR changed since the golden was recorded" >&2
    fi
done < <(grep -v '^#' "$FIX/corpus.txt")
echo "corpus (recorded): programs=${corpus_n} fail=${corpus_fail}"
fail=$((fail + corpus_fail))

# 4. Live comparison with the Python generator at <rev>.
if [[ "$mode" == "--python" ]]; then
    python_setup "$rev"
    { printf '%s\n' "${fixtures[@]}"
      find examples tests lib benchmarks compiler/fixtures -name '*.flow' -type f \
        | grep -v "^$FIX/" | LC_ALL=C sort; } > "$WORK/all.txt"
    accepted=0
    text_same=0
    text_fail=0
    gpu_same=0
    gpu_fail=0
    py_fail=0
    run_same=0
    run_fail=0
    run_skip=0
    run_nondet=0
    while IFS= read -r f; do
        key="$(key_of "$f")"
        flowc_emit "$f" "$WORK/flowc/$key.mlir" || continue
        accepted=$((accepted + 1))
        if ! python_emit "$f" "$WORK/python/$key.mlir"; then
            py_fail=$((py_fail + 1))
            echo "note: python@${rev} fails on $f (flowc accepts it)" >&2
            continue
        fi
        awk -f "$NORM" "$WORK/flowc/$key.mlir" > "$WORK/flowc/$key.norm"
        awk -f "$NORM" "$WORK/python/$key.mlir" > "$WORK/python/$key.norm"
        if cmp -s "$WORK/flowc/$key.norm" "$WORK/python/$key.norm"; then
            text_same=$((text_same + 1))
        else
            text_fail=$((text_fail + 1))
            echo "FAIL live $f: MLIR differs from python@${rev}" >&2
            diff "$WORK/python/$key.norm" "$WORK/flowc/$key.norm" | head -10 >&2 || true
            continue
        fi
        # A program with @gpu kernels: the GPU dialect module as well.
        if grep -q "^@gpu" "$f" \
            && python_emit "$f" "$WORK/python/$key.gpu.mlir" --mlir-gpu \
            && flowc_emit_gpu "$f" "$WORK/flowc/$key.gpu.mlir"; then
            awk -f "$NORM" "$WORK/flowc/$key.gpu.mlir" > "$WORK/flowc/$key.gpu.norm"
            awk -f "$NORM" "$WORK/python/$key.gpu.mlir" > "$WORK/python/$key.gpu.norm"
            if cmp -s "$WORK/flowc/$key.gpu.norm" "$WORK/python/$key.gpu.norm"; then
                gpu_same=$((gpu_same + 1))
            else
                gpu_fail=$((gpu_fail + 1))
                echo "FAIL live $f: GPU-mode MLIR differs from python@${rev}" >&2
            fi
        fi
        [[ "$have_mlir" -eq 1 ]] || continue
        # Run parity: both MLIR paths must build and agree, or both fail.
        flow_ok=1
        py_ok=1
        build_run "$WORK/flowc/$key" "$WORK/flowc/$key.mlir" mlir "$(dirname "$f")" || flow_ok=0
        if python_emit "$f" "$WORK/python/$key.ll" --llvm && [[ -s "$WORK/python/$key.ll" ]]; then
            build_run "$WORK/python/$key" "$WORK/python/$key.ll" ll "$(dirname "$f")" || py_ok=0
        else
            py_ok=0
        fi
        if [[ "$flow_ok" -eq 0 && "$py_ok" -eq 0 ]]; then
            run_skip=$((run_skip + 1))
        elif [[ "$flow_ok" -ne "$py_ok" ]]; then
            run_fail=$((run_fail + 1))
            echo "FAIL run $f: only one MLIR path built (flowc=${flow_ok} python=${py_ok})" >&2
        elif cmp -s "$WORK/flowc/$key.out" "$WORK/python/$key.out"; then
            run_same=$((run_same + 1))
        else
            # Timings and printed addresses change from run to run. A program
            # whose build disagrees with itself on a second run (either path)
            # is not comparable.
            run_exe "$WORK/python/$key" "$(dirname "$f")" "$WORK/python/$key.out2"
            run_exe "$WORK/flowc/$key" "$(dirname "$f")" "$WORK/flowc/$key.out2"
            if ! cmp -s "$WORK/python/$key.out" "$WORK/python/$key.out2" \
                || ! cmp -s "$WORK/flowc/$key.out" "$WORK/flowc/$key.out2"; then
                run_nondet=$((run_nondet + 1))
            else
                run_fail=$((run_fail + 1))
                echo "FAIL run $f: run output differs" >&2
                diff "$WORK/python/$key.out" "$WORK/flowc/$key.out" | head -10 >&2 || true
            fi
        fi
        rm -f "$WORK/flowc/$key.exe" "$WORK/python/$key.exe"
    done < "$WORK/all.txt"
    echo "live python@${rev}: accepted=${accepted} text_same=${text_same} text_fail=${text_fail} python_fail=${py_fail}"
    echo "live gpu dialect: same=${gpu_same} fail=${gpu_fail}"
    if [[ "$have_mlir" -eq 1 ]]; then
        echo "live run: same=${run_same} fail=${run_fail} nondeterministic=${run_nondet} both_unbuildable=${run_skip}"
    fi
    fail=$((fail + text_fail + gpu_fail + run_fail))
fi

if [[ "$fail" -ne 0 ]]; then
    echo "parity_mlir: FAIL (${fail})"
    exit 1
fi
echo "parity_mlir: PASS"
