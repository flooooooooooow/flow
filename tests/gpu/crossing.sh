#!/usr/bin/env bash
# WebGPU page parity gate: `wasm/crossings.sh gpu --no-build` and
# `wasm/crossings.sh shader`.
#
# Builds the WGSL half of the GPU crossing page (tools/gpu for the shaders,
# scripts/tools/wasm_crossings for the page) for each case below, with
# python and python3 stubbed out on PATH, and compares stdout, the exit
# status and every file written with tests/gpu/crossing/<case>/. The goldens
# were recorded from wasm/flow_wasm_gpu.py and wasm/flow_webgpu_shader.py
# of PARITY_REF:
#
#   tests/gpu/crossing.sh --record     # needs python3 and git
#
# The page now names tools/gpu/main.flow and `wasm/crossings.sh gpu` where it
# named the Python files; the recording applies that rename. The emcc build of
# the CPU reference (without --no-build) was checked byte for byte against
# the Python builder once (the .js and .wasm match); it needs emscripten, so
# the gate leaves it out.

set -uo pipefail

ROOT="$(cd "$(dirname "$0")/../.." && pwd -P)"
cd "$ROOT" || exit 1
PARITY_REF="${PARITY_REF:-fcd2edfe}"
EXP=tests/gpu/crossing
record=0
[[ "${1:-}" == "--record" ]] && record=1

work="$(mktemp -d "${TMPDIR:-/tmp}/flow-gpu-crossing.XXXXXX")"
work="$(cd "$work" && pwd -P)"
trap 'rm -rf "$work"' EXIT

tree="$ROOT"
if [[ "$record" -eq 1 ]]; then
    tree="$work/ref"
    mkdir -p "$tree"
    git archive "$PARITY_REF" wasm src lib compiler/scripts compiler/bootstrap examples | tar -x -C "$tree"
    mkdir -p "$tree/tests/gpu"
    cp -R tests/gpu/programs "$tree/tests/gpu/"
else
    stub="$work/bin"
    mkdir -p "$stub"
    for name in python python3; do
        printf '#!/bin/sh\necho "%s $*" >> "%s/python-calls.log"\nexit 127\n' "$name" "$work" > "$stub/$name"
        chmod +x "$stub/$name"
    done
    export PATH="$stub:$PATH"
fi

# name|command|arguments. `gpu` is the GPU crossing (--no-build);
# `shader` is the `shader fill` WebGPU page (wasm/flow_webgpu_shader.py).
cases=(
    "default|gpu|"
    "count|gpu|-n 4096"
    "stdlib_kernels|gpu|lib/stdlib/gpu_kernels.flow -n 1000"
    "no_kernels|gpu|tests/gpu/programs/no_gpu.flow"
    "wgsl_error|gpu|tests/gpu/programs/wgsl_err_cast.flow"
    "missing|gpu|tests/gpu/programs/missing.flow"
    "shader_gradient|shader|examples/gpu/vgpu/gradient.flow"
    "shader_named|shader|examples/gpu/shader_photoreal.flow --name photoreal_marble --size 320x200 --time 1.5"
    "shader_time_big|shader|examples/gpu/vgpu/gradient.flow --time 1e17"
    "shader_time_small|shader|examples/gpu/vgpu/gradient.flow --time 0.00001"
    "shader_bad_size|shader|examples/gpu/vgpu/gradient.flow --size 10"
    "shader_zero_size|shader|examples/gpu/vgpu/gradient.flow --size 0x5"
    "shader_bad_time|shader|examples/gpu/vgpu/gradient.flow --time abc"
    "shader_unknown_fill|shader|examples/gpu/vgpu/gradient.flow --name nope"
    "shader_no_fills|shader|tests/gpu/programs/no_gpu.flow"
    "shader_missing|shader|tests/gpu/programs/missing.flow"
)

pass=0
fail=0
for c in "${cases[@]}"; do
    name="${c%%|*}"
    rest="${c#*|}"
    cmd="${rest%%|*}"
    args="${rest#*|}"
    out_rel="site/wasm-crossings/gpu-gate"
    rm -rf "$tree/$out_rel"
    got="$work/got/$name"
    mkdir -p "$got/files"
    if [[ "$record" -eq 1 ]]; then
        if [[ "$cmd" == "gpu" ]]; then
            ( cd "$tree" && python3 wasm/flow_wasm_gpu.py $args --no-build --out "$out_rel" ) > "$got/stdout.raw" 2> "$work/stderr"
        else
            ( cd "$tree" && python3 wasm/flow_webgpu_shader.py $args --out "$out_rel" ) > "$got/stdout.raw" 2> "$work/stderr"
        fi
    elif [[ "$cmd" == "gpu" ]]; then
        ( cd "$tree" && wasm/crossings.sh gpu $args --no-build --out "$out_rel" ) > "$got/stdout.raw" 2> "$work/stderr"
    else
        ( cd "$tree" && wasm/crossings.sh shader $args --out "$out_rel" ) > "$got/stdout.raw" 2> "$work/stderr"
    fi
    echo $? > "$got/rc"
    sed "s|$tree|@ROOT@|g" "$got/stdout.raw" > "$got/stdout"
    rm -f "$got/stdout.raw"
    if [[ -d "$tree/$out_rel" ]]; then
        cp -R "$tree/$out_rel/." "$got/files/"
    fi
    rm -rf "$tree/$out_rel"
    if [[ "$record" -eq 1 ]]; then
        for f in "$got"/files/*; do
            [[ -f "$f" ]] && sed -i.bak -e 's|by src/flow/wgsl_codegen.py|by tools/gpu/main.flow|g' "$f" && rm -f "$f.bak"
        done
        if [[ -f "$got/files/index.html" ]]; then
            sed -i.bak -e 's|<code>src/flow/wgsl_codegen.py</code>|<code>tools/gpu/main.flow</code>|g' \
                -e 's|<code>wasm/flow_wasm_gpu.py</code>|<code>wasm/crossings.sh gpu</code>|' "$got/files/index.html"
            rm -f "$got/files/index.html.bak"
        fi
        rm -rf "$EXP/$name"
        mkdir -p "$EXP/$name"
        cp -R "$got/." "$EXP/$name/"
        echo "rec   $name"
        continue
    fi
    if diff -r "$EXP/$name" "$got" > "$work/diff.txt" 2>&1; then
        pass=$((pass + 1))
    else
        fail=$((fail + 1))
        echo "FAIL $name"
        head -20 "$work/diff.txt"
    fi
done

if [[ "$record" -eq 1 ]]; then
    exit 0
fi
if [[ -s "$work/python-calls.log" ]]; then
    echo "gpu crossing gate: python was called:"
    cat "$work/python-calls.log"
    fail=$((fail + 1))
fi
echo "gpu crossing gate: $pass passed, $fail failed"
[[ "$fail" -eq 0 ]]
