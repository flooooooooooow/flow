#!/usr/bin/env bash
# Dual CPU backends on the WASM page builder (`./flow tool wasm_build build`).
#
# The builder is the Flow program in scripts/tools/wasm_build. These tests
# drive it through its shim, so they cover the argument handling, the emcc
# command line and the pages it writes. The fake-emcc check needs only a C
# compiler; the real builds skip unless emcc works.
source "$(dirname "$0")/lib.sh"

wasm_build() { "$T_ROOT/flow" tool wasm_build build "$@"; }
HELLO="$T_ROOT/examples/wasm/hello_wasm.flow"
SNAKE="$T_ROOT/examples/games/snake_gfx.flow"

# emcc on PATH and `emcc -v` exits 0. Homebrew's emscripten needs these
# three variables when they are not already set.
emcc_ok() {
    command -v emcc > /dev/null 2>&1 || return 1
    (
        if [[ -z "${EMSDK_PYTHON:-}" && -e /opt/homebrew/bin/python3.14 ]]; then
            export EMSDK_PYTHON=/opt/homebrew/bin/python3.14
        fi
        if [[ -z "${EM_LLVM_ROOT:-}" && -e /opt/homebrew/opt/emscripten/libexec/llvm/bin ]]; then
            export EM_LLVM_ROOT=/opt/homebrew/opt/emscripten/libexec/llvm/bin
        fi
        if [[ -z "${EM_BINARYEN_ROOT:-}" && -e /opt/homebrew/opt/emscripten/libexec/binaryen ]]; then
            export EM_BINARYEN_ROOT=/opt/homebrew/opt/emscripten/libexec/binaryen
        fi
        emcc -v > /dev/null 2>&1
    )
}
EMCC_OK=0
if emcc_ok; then
    EMCC_OK=1
fi

need_emcc() {
    [[ "$EMCC_OK" -eq 1 ]] || t_skip "emcc not usable"
}

check_backend_from_environment_is_validated() {
    t_need_cc
    FLOW_CPU_BACKEND=spirv t_run wasm_build "$HELLO" --out "$T_TMP"
    a_eq "$T_RC" 1 "exit status"
    a_file_is "$T_ERR" $'error: unknown backend \'spirv\' (expected c|mlir)\n'
}

check_backend_choice_is_checked_by_the_parser() {
    t_need_cc
    t_run wasm_build "$HELLO" --backend spirv
    a_eq "$T_RC" 2 "exit status"
    a_file_contains "$T_ERR" "invalid choice: 'spirv' (choose from c, mlir)"
}

# A fake emcc records the command line the builder hands it.
check_emcc_command_preload_link_and_opt() {
    t_need_cc
    [[ -e "$HELLO" ]] || t_skip "hello_wasm.flow missing"
    mkdir -p "$T_TMP/bin"
    local log="$T_TMP/argv.txt"
    {
        printf '#!/bin/sh\n'
        printf '[ "$1" = "-v" ] && exit 0\n'
        printf 'for a in "$@"; do printf "%%s\\n" "$a"; done > "%s"\n' "$log"
        printf 'echo "emcc: error: fake emcc" >&2\n'
        printf 'exit 1\n'
    } > "$T_TMP/bin/emcc"
    chmod 755 "$T_TMP/bin/emcc"
    local support="$T_ROOT/runtime/flow_rt_support.c"
    PATH="$T_TMP/bin:$PATH" t_run wasm_build "$HELLO" \
        --out "$T_TMP/out" \
        -O1 \
        --preload /tmp/data@/data \
        --link "$support" \
        --link runtime/gfx_macos.m \
        --initial-memory 64MB
    a_eq "$T_RC" 1 "exit status"
    a_file_is "$T_ERR" $'error: emcc: error: fake emcc\n'
    a_true "-sFORCE_FILESYSTEM=1 in argv" grep -qxF -- -sFORCE_FILESYSTEM=1 "$log"
    local after_preload
    after_preload="$(awk 'prev == "--preload-file" { print; exit } { prev = $0 }' "$log")"
    a_eq "$after_preload" "/tmp/data@/data" "argument after --preload-file"
    local resolved
    resolved="$(cd "$(dirname "$support")" && pwd -P)/$(basename "$support")"
    a_true "$resolved in argv" grep -qxF -- "$resolved" "$log"
    a_true "no .m file in argv" test -z "$(grep -E '\.m$' "$log" || true)"
    a_true "-sINITIAL_MEMORY=64MB in argv" grep -qxF -- -sINITIAL_MEMORY=64MB "$log"
    a_true "-O1 in argv" grep -qxF -- -O1 "$log"
}

check_wasm_build_backend() {
    local backend="$1"
    t_need_cc
    [[ -e "$HELLO" ]] || t_skip "hello_wasm.flow missing"
    need_emcc
    local out="$T_TMP/$backend"
    t_run wasm_build "$HELLO" --out "$out" --backend "$backend" -O1 --json
    [[ "$T_RC" -eq 0 ]] || { cat "$T_ERR"; return 1; }
    a_eq "$(jq -r .backend "$T_OUT")" "$backend" "json backend"
    a_exists "$out/hello_wasm.wasm"
    a_exists "$out/hello_wasm.js"
    if [[ "$backend" == mlir ]]; then
        a_file_contains "$out/index.html" "MLIR"
    else
        a_file_contains "$out/index.html" "C &rarr; WebAssembly"
    fi
}

check_wasm_build_preload_emits_data() {
    local backend="$1"
    t_need_cc
    [[ -e "$HELLO" ]] || t_skip "hello_wasm.flow missing"
    need_emcc
    mkdir -p "$T_TMP/pack"
    printf 'hello from preload\n' > "$T_TMP/pack/note.txt"
    local out="$T_TMP/out-$backend"
    t_run wasm_build "$HELLO" --out "$out" --backend "$backend" -O1 \
        --preload "$T_TMP/pack@/data" \
        --link "$T_ROOT/runtime/flow_rt_support.c" \
        --json
    [[ "$T_RC" -eq 0 ]] || { cat "$T_ERR"; return 1; }
    a_eq "$(jq -r .backend "$T_OUT")" "$backend" "json backend"
    a_exists "$out/hello_wasm.wasm"
    a_exists "$out/hello_wasm.data"
    a_eq "$(jq '(.data_bytes // 0) > 0' "$T_OUT")" true "data_bytes > 0"
}

# Epic #221: MLIR backend builds a gfx+ASYNCIFY canvas page.
check_wasm_mlir_gfx_snake() {
    t_need_cc
    [[ -e "$SNAKE" ]] || t_skip "snake_gfx.flow missing"
    need_emcc
    local out="$T_TMP/snake-mlir"
    t_run wasm_build "$SNAKE" --out "$out" --backend mlir -O1 --json
    [[ "$T_RC" -eq 0 ]] || { cat "$T_ERR"; return 1; }
    a_eq "$(jq -r .backend "$T_OUT")" mlir "json backend"
    a_eq "$(jq '.gfx == true' "$T_OUT")" true "json gfx is true"
    a_exists "$out/snake_gfx.wasm"
    a_file_contains "$out/index.html" "MLIR"
    a_true "canvas in index.html" grep -qi canvas "$out/index.html"
}

t_check backend_from_environment_is_validated check_backend_from_environment_is_validated
t_check backend_choice_is_checked_by_the_parser check_backend_choice_is_checked_by_the_parser
t_check emcc_command_preload_link_and_opt check_emcc_command_preload_link_and_opt
t_check "wasm_build_both_backends[c]" check_wasm_build_backend c
t_check "wasm_build_both_backends[mlir]" check_wasm_build_backend mlir
t_check "wasm_build_preload_emits_data[c]" check_wasm_build_preload_emits_data c
t_check "wasm_build_preload_emits_data[mlir]" check_wasm_build_preload_emits_data mlir
t_check wasm_mlir_gfx_snake check_wasm_mlir_gfx_snake
t_done
