#!/usr/bin/env bash
# Parity gate for `flow bpf` and `flow wasm32` (scripts/tools/llvm_target).
#
# Runs every case in tests/targets/cases.txt through scripts/bpf_target.sh or
# scripts/wasm32_target.sh with stub `python` and `python3` first on PATH
# (each logs its arguments and exits 127), and compares the exit status,
# stderr and the SHA-256 of the written object with the goldens in
# tests/targets/expected. The goldens were captured from the Python modules
# this tool replaced (src/flow/bpf_target.py, src/flow/wasm_compiler.py).
#
# Normalisation, applied to the tool's stderr before comparing:
#   - exit status 2 (usage errors): only the "error:" line, without the
#     program name (argparse printed `bpf_target.py: error: ...`);
#   - the case's output directory reads @OUTDIR@;
#   - compare=first cases keep only the first line (the rest is compiler
#     diagnostics from the lowering, which name a different front end).
#
# Needs clang with the BPF and WebAssembly targets, wasm-ld, mlir-opt and
# mlir-translate (Homebrew llvm on macOS; LLVM_PATH or PATH elsewhere).
#
#   compiler/scripts/parity_targets.sh

set -uo pipefail

ROOT="$(cd "$(dirname "$0")/../.." && pwd -P)"
cd "$ROOT" || exit 1

if command -v brew >/dev/null 2>&1; then
    llvm_prefix="$(brew --prefix llvm 2>/dev/null || true)"
    if [[ -n "$llvm_prefix" && -x "$llvm_prefix/bin/clang" ]]; then
        export PATH="$llvm_prefix/bin:$PATH"
    fi
fi
if [[ -n "${LLVM_PATH:-}" ]]; then
    export PATH="$LLVM_PATH:$PATH"
fi

work="$(mktemp -d "${TMPDIR:-/tmp}/flow-targets.XXXXXX")"
trap 'rm -rf "$work"' EXIT
stub_dir="$work/bin"
log="$work/python-calls.log"
mkdir -p "$stub_dir" "$work/out"
: > "$log"
for name in python python3; do
    printf '#!/bin/sh\necho "%s $*" >> "%s"\nexit 127\n' "$name" "$log" > "$stub_dir/$name"
    chmod +x "$stub_dir/$name"
done
export PATH="$stub_dir:$PATH"

# Build the tool once, outside the timed cases.
if ! scripts/tools/build_tool.sh llvm_target >/dev/null; then
    echo "parity_targets: could not build scripts/tools/llvm_target" >&2
    exit 1
fi

exp=tests/targets/expected
pass=0
fail=0
while IFS='|' read -r name tool cmp args; do
    name="$(echo "$name" | tr -d '[:space:]')"
    tool="$(echo "$tool" | tr -d '[:space:]')"
    cmp="$(echo "$cmp" | tr -d '[:space:]')"
    [[ -z "$name" || "$name" == \#* ]] && continue
    out="$work/out/$name.out"
    argv=()
    for a in $args; do
        a="${a//@OUT@/$out}"
        a="${a//@SP@/ }"
        argv+=("$(printf '%b' "$a")")
    done
    rc=0
    "scripts/${tool}_target.sh" "${argv[@]+"${argv[@]}"}" 2>"$work/$name.raw" || rc=$?
    if [[ "$rc" -eq 2 ]]; then
        grep -E ': error: ' "$work/$name.raw" | sed -E 's/^[^:]*: error: /error: /' > "$work/$name.err"
    else
        cp "$work/$name.raw" "$work/$name.err"
    fi
    sed -i.bak "s#$work/out/#@OUTDIR@/#g" "$work/$name.err"
    expected_err="$work/$name.expected"
    cp "$exp/$name.err" "$expected_err"
    if [[ "$cmp" == first ]]; then
        head -1 "$work/$name.err" > "$work/$name.err1" && mv "$work/$name.err1" "$work/$name.err"
        head -1 "$expected_err" > "$expected_err.1" && mv "$expected_err.1" "$expected_err"
    fi
    sha=none
    [[ -f "$out" ]] && sha="$(shasum -a 256 "$out" | cut -d' ' -f1)"
    problems=""
    [[ "$rc" == "$(cat "$exp/$name.rc")" ]] || problems+=" exit $rc (want $(cat "$exp/$name.rc"))"
    [[ "$sha" == "$(cat "$exp/$name.sha")" ]] || problems+=" output sha differs"
    cmp -s "$work/$name.err" "$expected_err" || problems+=" stderr differs"
    if [[ -z "$problems" ]]; then
        pass=$((pass + 1))
    else
        fail=$((fail + 1))
        echo "FAIL $name:$problems"
        diff "$expected_err" "$work/$name.err" | head -20 | sed 's/^/    /'
    fi
done < tests/targets/cases.txt

if [[ -s "$log" ]]; then
    echo "FAIL python was called:"
    sed 's/^/    /' "$log"
    fail=$((fail + 1))
fi
echo "parity_targets: pass=$pass fail=$fail"
[[ "$fail" -eq 0 ]]
