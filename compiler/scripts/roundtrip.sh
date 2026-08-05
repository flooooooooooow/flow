#!/usr/bin/env bash
# Stage-A flowc emit → clang → run for each fixture; check expected exit codes.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
cd "$ROOT"
mkdir -p compiler/build

# Emit Flow → C. Prefer Stage-A Flow driver when built (fast, low mem); else
# Python host bootstrap for latest Stage-A sources. Force host with FLOWC_FORCE_HOST=1
# after editing compiler/src/*.flow before rebuilding the frontend objects.
stage_a_emit() {
    local src="$1"
    local c_out="$2"
    if [[ "${FLOWC_FORCE_HOST:-}" == "1" ]] && [[ -f compiler/src/main.flow ]]; then
        export FLOWC_IN="$src"
        export FLOWC_OUT="$c_out"
        ./flow run compiler/src/main.flow
    elif [[ -x compiler/build/stage_a_driver_flow ]]; then
        ./compiler/build/stage_a_driver_flow "$src" "$c_out"
    elif [[ -x compiler/build/stage_a_driver ]]; then
        ./compiler/build/stage_a_driver "$src" "$c_out"
    elif [[ -f compiler/src/main.flow ]]; then
        export FLOWC_IN="$src"
        export FLOWC_OUT="$c_out"
        ./flow run compiler/src/main.flow
    else
        echo "FAIL stage_a_emit: no emitter (compiler/src/main.flow or stage_a_driver*)" >&2
        return 1
    fi
}

run_case() {
    local name="$1"
    local expect="$2"
    local fixture="compiler/fixtures/${name}.flow"
    local c_out="compiler/build/${name}.c"
    local bin="compiler/build/${name}"

    echo "=== ${name} ==="
    stage_a_emit "$fixture" "$c_out"
    cc -O0 -o "$bin" "$c_out"
    set +e
    "./$bin"
    local code=$?
    set -e
    echo "exit=$code"
    test "$code" -eq "$expect"
    echo "PASS ${name}"
}

# Compile a real flowc module to a C object (no link/run — modules have no main).
# Optional further args: header paths for `cc -include` (imported sibling types/consts).
# Frontend dogfood opts out of Stage-A typecheck (imports/extern not fully resolved).
compile_module() {
    local name="$1"
    local src="$2"
    shift 2
    local c_out="compiler/build/${name}_flowc.c"
    local obj="compiler/build/${name}_flowc.o"
    local -a cc_args=(-O0 -c)

    echo "=== compile_module ${name} ==="
    # Always host-emit frontend modules so edits to compiler/src are picked up
    # even when a stale stage_a_driver_flow binary exists from a prior roundtrip.
    FLOWC_TYPECHECK=0 FLOWC_FORCE_HOST=1 stage_a_emit "$src" "$c_out"
    local h
    for h in "$@"; do
        cc_args+=(-include "$h")
    done
    cc "${cc_args[@]}" "$c_out" -o "$obj"
    echo "PASS compile_module ${name}"
}

run_case stage_a_sum 45
run_case stage_a_for_sum 45
run_case stage_a_for_dotdot 45
if ! grep -Fq 'for (int32_t i = 0; i < 10; i = i + 1)' compiler/build/stage_a_for_dotdot.c; then
    echo "FAIL stage_a_for_dotdot: expected C for-loop from 0..10 range" >&2
    exit 1
fi
run_case stage_a_const 12
run_case stage_a_struct 42
# Dogfood: token.flow const subset (requires AST_CONST=31 emit).
# Export consts are non-static `const int32_t` for multi-module linkage.
run_case stage_a_token_consts 29
if ! grep -q 'const int32_t' compiler/build/stage_a_token_consts.c; then
    echo "FAIL stage_a_token_consts: const emit missing (expected const int32_t; AST_CONST=31)" >&2
    exit 1
fi
if grep -q 'static const int32_t' compiler/build/stage_a_token_consts.c; then
    echo "FAIL stage_a_token_consts: export const should be non-static" >&2
    exit 1
fi
# Dogfood: Token struct + flowc_make_tok (struct return type).
run_case stage_a_token_struct 26
# ptr<i32> params/lets + unary & + index (exit 40+2).
run_case stage_a_ptr 42
# expr as Type casts (exit 42).
run_case stage_a_cast 42
# indexed assign p[0] = n (exit 42).
run_case stage_a_index_assign 42
# array init + while + % + if/else + puts("…") (exit 42).
run_case stage_a_array_else 42
if ! grep -Fq '} else {' compiler/build/stage_a_array_else.c; then
    echo "FAIL stage_a_array_else: expected clean '} else {' emit" >&2
    exit 1
fi
if ! grep -Fq 'int32_t a[4] = { 10, 20, 30, 5 };' compiler/build/stage_a_array_else.c; then
    echo "FAIL stage_a_array_else: array local init missing" >&2
    exit 1
fi
if ! grep -Fq 'puts("ok")' compiler/build/stage_a_array_else.c; then
    echo "FAIL stage_a_array_else: string literal in call missing" >&2
    exit 1
fi
if ! grep -Fq ' % ' compiler/build/stage_a_array_else.c; then
    echo "FAIL stage_a_array_else: modulo emit missing" >&2
    exit 1
fi
# Recursive fibonacci (examples/basics/fibonacci.flow twin) → exit 55.
run_case stage_a_fib 55

# First real module dogfood: emit + compile-object compiler/src/token.flow
# (export struct/function unwrap, ptr<u8> field types).
compile_module token compiler/src/token.flow
# -F: treat needles as fixed strings ('*' in uint8_t* must not be BRE).
for needle in 'typedef struct Token' 'flowc_make_tok' 'uint8_t* input'; do
    if ! grep -Fq "$needle" compiler/build/token_flowc.c; then
        echo "FAIL compile_module token: missing '${needle}' in emitted C" >&2
        exit 1
    fi
done
echo "PASS compile_module token greps"

# Second module dogfood: ast.flow (casts, indexed field assign, void returns).
compile_module ast compiler/src/ast.flow
for needle in 'flowc_ast_new' 'typedef struct AstNode' 'AstArena'; do
    if ! grep -Fq "$needle" compiler/build/ast_flowc.c; then
        echo "FAIL compile_module ast: missing '${needle}' in emitted C" >&2
        exit 1
    fi
done
echo "PASS compile_module ast greps"

# Third module: lexer.flow (imports .token — skipped at emit; -include token header).
python3 compiler/scripts/flowc_c_to_hdr.py \
    compiler/build/token_flowc.c compiler/build/token_flowc.h
compile_module lexer compiler/src/lexer.flow compiler/build/token_flowc.h
for needle in 'flowc_lexer_new' 'flowc_lexer_next' 'flowc_lex_classify_keyword'; do
    if ! grep -Fq "$needle" compiler/build/lexer_flowc.c; then
        echo "FAIL compile_module lexer: missing '${needle}' in emitted C" >&2
        exit 1
    fi
done
# Linkability smoke: both objects resolve (no main — relocatable link).
cc -r -o compiler/build/token_lexer_flowc.o \
    compiler/build/token_flowc.o compiler/build/lexer_flowc.o
if ! nm compiler/build/lexer_flowc.o | grep -q 'flowc_lexer_next'; then
    echo "FAIL compile_module lexer: flowc_lexer_next missing from object" >&2
    exit 1
fi
if ! nm compiler/build/token_flowc.o | grep -q 'TOK_EOF'; then
    echo "FAIL compile_module lexer: TOK_EOF missing from token object" >&2
    exit 1
fi
echo "PASS compile_module lexer greps+link"

# Fourth module: fileio.flow (extern → #include <stdio.h>; null → NULL; string → const char*).
compile_module fileio compiler/src/fileio.flow
for needle in 'flowc_read_file' 'flowc_write_file' '#include <stdio.h>' 'NULL' 'const char*'; do
    if ! grep -Fq "$needle" compiler/build/fileio_flowc.c; then
        echo "FAIL compile_module fileio: missing '${needle}' in emitted C" >&2
        exit 1
    fi
done
if ! grep -q 'static const int32_t FLOWC_IO_SEEK_SET' compiler/build/fileio_flowc.c; then
    echo "FAIL compile_module fileio: non-export const should be static" >&2
    exit 1
fi
echo "PASS compile_module fileio greps"

# Fifth module: parser.flow (imports token/ast/lexer — -include their headers).
python3 compiler/scripts/flowc_c_to_hdr.py \
    compiler/build/ast_flowc.c compiler/build/ast_flowc.h
python3 compiler/scripts/flowc_c_to_hdr.py \
    compiler/build/lexer_flowc.c compiler/build/lexer_flowc.h
compile_module parser compiler/src/parser.flow \
    compiler/build/token_flowc.h \
    compiler/build/ast_flowc.h \
    compiler/build/lexer_flowc.h
for needle in 'flowc_parser_new' 'flowc_parse_program' 'typedef struct Parser'; do
    if ! grep -Fq "$needle" compiler/build/parser_flowc.c; then
        echo "FAIL compile_module parser: missing '${needle}' in emitted C" >&2
        exit 1
    fi
done
# Prototypes for mutual-recursion forward decls.
if ! grep -Fq 'int32_t flowc_parse_expr(Parser* p);' compiler/build/parser_flowc.c; then
    echo "FAIL compile_module parser: forward-decl prototype missing" >&2
    exit 1
fi
echo "PASS compile_module parser greps"

# Sixth module: cgen.flow (imports token/ast — -include their headers; extern → string.h).
compile_module cgen compiler/src/cgen.flow \
    compiler/build/token_flowc.h \
    compiler/build/ast_flowc.h
for needle in 'flowc_cgen_emit' 'flowc_cgen_emit_ex' 'typedef struct CgenBuf' '#include <string.h>' ' % '; do
    if ! grep -Fq "$needle" compiler/build/cgen_flowc.c; then
        echo "FAIL compile_module cgen: missing '${needle}' in emitted C" >&2
        exit 1
    fi
done
# Prototypes for mutual-recursion forward decls (emit_expr/stmt/block).
if ! grep -Fq 'void flowc_cgen_emit_expr(CgenBuf* w, AstArena arena, uint8_t* src, int32_t id);' compiler/build/cgen_flowc.c; then
    echo "FAIL compile_module cgen: forward-decl prototype missing" >&2
    exit 1
fi
echo "PASS compile_module cgen greps"

# Seventh module: typecheck.flow (imports ast — -include ast header).
compile_module typecheck compiler/src/typecheck.flow \
    compiler/build/ast_flowc.h
for needle in 'flowc_typecheck' 'flowc_tc_init' 'flowc_tc_seed_export' 'flowc_tc_check_program' 'typedef struct TcCtx' 'seed_nlen'; do
    if ! grep -Fq "$needle" compiler/build/typecheck_flowc.c; then
        echo "FAIL compile_module typecheck: missing '${needle}' in emitted C" >&2
        exit 1
    fi
done
echo "PASS compile_module typecheck greps"

# Eighth module: resolve.flow (imports ast/parser/fileio/cgen/typecheck).
python3 compiler/scripts/flowc_c_to_hdr.py \
    compiler/build/parser_flowc.c compiler/build/parser_flowc.h
python3 compiler/scripts/flowc_c_to_hdr.py \
    compiler/build/fileio_flowc.c compiler/build/fileio_flowc.h
python3 compiler/scripts/flowc_c_to_hdr.py \
    compiler/build/cgen_flowc.c compiler/build/cgen_flowc.h
python3 compiler/scripts/flowc_c_to_hdr.py \
    compiler/build/typecheck_flowc.c compiler/build/typecheck_flowc.h
compile_module resolve compiler/src/resolve.flow \
    compiler/build/token_flowc.h \
    compiler/build/ast_flowc.h \
    compiler/build/lexer_flowc.h \
    compiler/build/parser_flowc.h \
    compiler/build/fileio_flowc.h \
    compiler/build/cgen_flowc.h \
    compiler/build/typecheck_flowc.h
for needle in 'flowc_bundle_emit' 'flowc_bundle_typecheck' 'flowc_resolve_sibling_path' 'flowc_resolve_dirname'; do
    if ! grep -Fq "$needle" compiler/build/resolve_flowc.c; then
        echo "FAIL compile_module resolve: missing '${needle}' in emitted C" >&2
        exit 1
    fi
done
echo "PASS compile_module resolve greps"

# Optional backends (kept out of flowc_frontend.o / self-host fixed-point):
# jsgen.flow + fmt.flow — emit→cc -c + separate relocatable link with token/ast.
compile_module jsgen compiler/src/jsgen.flow \
    compiler/build/token_flowc.h \
    compiler/build/ast_flowc.h
for needle in 'flowc_jsgen_emit' 'typedef struct JsgenBuf'; do
    if ! grep -Fq "$needle" compiler/build/jsgen_flowc.c; then
        echo "FAIL compile_module jsgen: missing '${needle}' in emitted C" >&2
        exit 1
    fi
done
echo "PASS compile_module jsgen greps"

compile_module fmt compiler/src/fmt.flow \
    compiler/build/token_flowc.h \
    compiler/build/ast_flowc.h
for needle in 'flowc_fmt_emit' 'typedef struct FmtBuf'; do
    if ! grep -Fq "$needle" compiler/build/fmt_flowc.c; then
        echo "FAIL compile_module fmt: missing '${needle}' in emitted C" >&2
        exit 1
    fi
done
echo "PASS compile_module fmt greps"

cc -r -o compiler/build/flowc_jsgen_fmt.o \
    compiler/build/token_flowc.o \
    compiler/build/ast_flowc.o \
    compiler/build/jsgen_flowc.o \
    compiler/build/fmt_flowc.o
for sym in flowc_jsgen_emit flowc_fmt_emit; do
    if ! nm compiler/build/flowc_jsgen_fmt.o | grep -q "$sym"; then
        echo "FAIL jsgen/fmt link smoke: ${sym} missing from flowc_jsgen_fmt.o" >&2
        exit 1
    fi
done
echo "PASS link smoke flowc_jsgen_fmt.o"

# FLOWC_BACKEND=js / fmt fixture smokes (host emit via main.flow).
echo "=== jsgen fixture smoke (FLOWC_BACKEND=js) ==="
FLOWC_BACKEND=js FLOWC_IN=compiler/fixtures/stage_a_sum.flow \
FLOWC_OUT=compiler/build/stage_a_sum.js \
    ./flow run compiler/src/main.flow
for needle in 'function' 'return'; do
    if ! grep -Fq "$needle" compiler/build/stage_a_sum.js; then
        echo "FAIL jsgen fixture: missing '${needle}' in stage_a_sum.js" >&2
        exit 1
    fi
done
if command -v node >/dev/null 2>&1; then
    # Syntax check only (JS has no top-level call of main).
    node --check compiler/build/stage_a_sum.js
fi
echo "PASS jsgen fixture smoke"

echo "=== fmt fixture smoke (FLOWC_BACKEND=fmt) ==="
FLOWC_BACKEND=fmt FLOWC_IN=compiler/fixtures/stage_a_sum.flow \
FLOWC_OUT=compiler/build/stage_a_sum.fmt.flow \
    ./flow run compiler/src/main.flow
if ! grep -Fq 'function' compiler/build/stage_a_sum.fmt.flow; then
    echo "FAIL fmt fixture: missing pretty-printed 'function'" >&2
    exit 1
fi
echo "PASS fmt fixture smoke"

# Multi-file link smoke: emit math.flow + main.flow (import skipped) → exit 42.
FLOWC_RESOLVE_IMPORTS=1 ./compiler/scripts/stage_a_link_two.sh

# Multi-file bundle: FLOWC_BUNDLE=1 resolves .bundle_lib → one TU → exit 42.
# Default typecheck ON runs flowc_bundle_typecheck (deps-first + export seed).
# Host-emit: needs latest resolve/typecheck (stale driver_flow may predate bundle TC).
# Note: agent sandbox cannot exec-verify binaries; local runs should still cc+run.
echo "=== FLOWC_BUNDLE fixtures ==="
FLOWC_FORCE_HOST=1 FLOWC_BUNDLE=1 FLOWC_DIR=compiler/fixtures \
    stage_a_emit \
    compiler/fixtures/bundle_main.flow \
    compiler/build/bundle_main.c
if ! grep -Fq 'twice' compiler/build/bundle_main.c; then
    echo "FAIL FLOWC_BUNDLE: expected twice from bundle_lib in bundled C" >&2
    exit 1
fi
if ! grep -Fq 'int32_t N' compiler/build/bundle_main.c; then
    echo "FAIL FLOWC_BUNDLE: expected const N from bundle_lib" >&2
    exit 1
fi
# Includes only once (deps after the first use emit_ex flags&1).
stdint_n=$(grep -c '#include <stdint.h>' compiler/build/bundle_main.c || true)
if [[ "$stdint_n" -ne 1 ]]; then
    echo "FAIL FLOWC_BUNDLE: expected exactly one stdint include, got ${stdint_n}" >&2
    exit 1
fi
cc -O0 -o compiler/build/bundle_main compiler/build/bundle_main.c
set +e
./compiler/build/bundle_main
bundle_code=$?
set -e
echo "bundle_main exit=$bundle_code"
test "$bundle_code" -eq 42

# bundle_tc_ok: same shape as bundle_main; default typecheck + bundle emit.
FLOWC_FORCE_HOST=1 FLOWC_BUNDLE=1 FLOWC_DIR=compiler/fixtures \
    stage_a_emit \
    compiler/fixtures/bundle_tc_ok.flow \
    compiler/build/bundle_tc_ok.c
if [[ ! -f compiler/build/bundle_tc_ok.c ]]; then
    echo "FAIL FLOWC_BUNDLE: bundle_tc_ok should emit with default typecheck" >&2
    exit 1
fi

# bundle_tc_bad: undefined no_such → bundle typecheck fails (no C written).
rm -f compiler/build/bundle_tc_bad.c
set +e
FLOWC_FORCE_HOST=1 FLOWC_BUNDLE=1 FLOWC_DIR=compiler/fixtures \
    stage_a_emit \
    compiler/fixtures/bundle_tc_bad.flow \
    compiler/build/bundle_tc_bad.c
bundle_bad_rc=$?
set -e
echo "bundle_tc_bad emit rc=$bundle_bad_rc"
test "$bundle_bad_rc" -ne 0
if [[ -f compiler/build/bundle_tc_bad.c ]]; then
    echo "FAIL FLOWC_BUNDLE: bundle_tc_bad should not write C when typecheck on" >&2
    exit 1
fi
# Opt-out still emits the bad fixture (bundle typecheck skipped).
FLOWC_FORCE_HOST=1 FLOWC_BUNDLE=1 FLOWC_DIR=compiler/fixtures \
FLOWC_TYPECHECK=0 \
    stage_a_emit \
    compiler/fixtures/bundle_tc_bad.flow \
    compiler/build/bundle_tc_bad_optout.c
if [[ ! -f compiler/build/bundle_tc_bad_optout.c ]]; then
    echo "FAIL FLOWC_TYPECHECK=0: expected bundle_tc_bad opt-out emit to write C" >&2
    exit 1
fi
echo "PASS FLOWC_BUNDLE fixtures"

# Real frontend pair: FLOWC_BUNDLE=1 emits token.flow then lexer.flow in one TU
# (deps first). No flowc_c_to_hdr.py / cc -include — Token/TOK_* live in the same file.
echo "=== FLOWC_BUNDLE lexer (token+lexer one TU) ==="
FLOWC_FORCE_HOST=1 FLOWC_BUNDLE=1 FLOWC_DIR=compiler/src \
FLOWC_TYPECHECK=0 \
    stage_a_emit compiler/src/lexer.flow compiler/build/bundle_lexer.c
if ! grep -Fq 'typedef struct Token' compiler/build/bundle_lexer.c; then
    echo "FAIL FLOWC_BUNDLE lexer: expected Token from token.flow in bundled C" >&2
    exit 1
fi
if ! grep -Fq 'flowc_lexer_next' compiler/build/bundle_lexer.c; then
    echo "FAIL FLOWC_BUNDLE lexer: expected flowc_lexer_next from lexer.flow" >&2
    exit 1
fi
bundle_lexer_stdint=$(grep -c '#include <stdint.h>' compiler/build/bundle_lexer.c || true)
if [[ "$bundle_lexer_stdint" -ne 1 ]]; then
    echo "FAIL FLOWC_BUNDLE lexer: expected exactly one stdint include, got ${bundle_lexer_stdint}" >&2
    exit 1
fi
cc -O0 -c compiler/build/bundle_lexer.c -o compiler/build/bundle_lexer.o
if ! nm compiler/build/bundle_lexer.o | grep -q 'flowc_lexer_next'; then
    echo "FAIL FLOWC_BUNDLE lexer: flowc_lexer_next missing from object" >&2
    exit 1
fi
if ! nm compiler/build/bundle_lexer.o | grep -q 'TOK_EOF'; then
    echo "FAIL FLOWC_BUNDLE lexer: TOK_EOF missing from object" >&2
    exit 1
fi
echo "PASS FLOWC_BUNDLE lexer (token+lexer one TU)"

# Frontend parser bundle: FLOWC_BUNDLE=1 emits token+ast+lexer+parser in one TU
# (deps first). Needs 1MB out_cap in main/driver. No flowc_c_to_hdr.py / -include.
echo "=== FLOWC_BUNDLE parser (token+ast+lexer+parser one TU) ==="
FLOWC_FORCE_HOST=1 FLOWC_BUNDLE=1 FLOWC_DIR=compiler/src \
FLOWC_TYPECHECK=0 \
    stage_a_emit compiler/src/parser.flow compiler/build/bundle_parser.c
if ! grep -Fq 'flowc_parse_program' compiler/build/bundle_parser.c; then
    echo "FAIL FLOWC_BUNDLE parser: expected flowc_parse_program from parser.flow" >&2
    exit 1
fi
if ! grep -Fq 'typedef struct AstNode' compiler/build/bundle_parser.c; then
    echo "FAIL FLOWC_BUNDLE parser: expected AstNode from ast.flow in bundled C" >&2
    exit 1
fi
if ! grep -Fq 'typedef struct Token' compiler/build/bundle_parser.c; then
    echo "FAIL FLOWC_BUNDLE parser: expected Token from token.flow in bundled C" >&2
    exit 1
fi
if ! grep -Fq 'flowc_lexer_next' compiler/build/bundle_parser.c; then
    echo "FAIL FLOWC_BUNDLE parser: expected flowc_lexer_next from lexer.flow" >&2
    exit 1
fi
bundle_parser_stdint=$(grep -c '#include <stdint.h>' compiler/build/bundle_parser.c || true)
if [[ "$bundle_parser_stdint" -ne 1 ]]; then
    echo "FAIL FLOWC_BUNDLE parser: expected exactly one stdint include, got ${bundle_parser_stdint}" >&2
    exit 1
fi
cc -O0 -c compiler/build/bundle_parser.c -o compiler/build/bundle_parser.o
if ! nm compiler/build/bundle_parser.o | grep -q 'flowc_parse_program'; then
    echo "FAIL FLOWC_BUNDLE parser: flowc_parse_program missing from object" >&2
    exit 1
fi
if ! nm compiler/build/bundle_parser.o | grep -q 'flowc_lexer_next'; then
    echo "FAIL FLOWC_BUNDLE parser: flowc_lexer_next missing from object" >&2
    exit 1
fi
echo "PASS FLOWC_BUNDLE parser (token+ast+lexer+parser one TU)"

# Default-ON typecheck fixtures (host emit — picks up latest main.flow semantics
# before stage_a_driver_flow is rebuilt later in this script).
echo "=== FLOWC_TYPECHECK fixtures (default on) ==="
FLOWC_FORCE_HOST=1 stage_a_emit \
    compiler/fixtures/typecheck_ok.flow \
    compiler/build/typecheck_ok.c
cc -O0 -o compiler/build/typecheck_ok compiler/build/typecheck_ok.c
set +e
./compiler/build/typecheck_ok
tc_ok_code=$?
set -e
echo "typecheck_ok exit=$tc_ok_code"
test "$tc_ok_code" -eq 42
rm -f compiler/build/typecheck_undef.c
set +e
FLOWC_FORCE_HOST=1 stage_a_emit \
    compiler/fixtures/typecheck_undef.flow \
    compiler/build/typecheck_undef.c
tc_bad_rc=$?
set -e
echo "typecheck_undef emit rc=$tc_bad_rc"
test "$tc_bad_rc" -ne 0
if [[ -f compiler/build/typecheck_undef.c ]]; then
    echo "FAIL FLOWC_TYPECHECK: undef fixture should not write C" >&2
    exit 1
fi
# Opt-out still emits the undef fixture (typecheck skipped).
FLOWC_FORCE_HOST=1 FLOWC_TYPECHECK=0 stage_a_emit \
    compiler/fixtures/typecheck_undef.flow \
    compiler/build/typecheck_undef_optout.c
if [[ ! -f compiler/build/typecheck_undef_optout.c ]]; then
    echo "FAIL FLOWC_TYPECHECK=0: expected opt-out emit to write C" >&2
    exit 1
fi
echo "PASS FLOWC_TYPECHECK fixtures"

# Link smoke: all frontend modules resolve into one relocatable object.
cc -r -o compiler/build/flowc_frontend.o \
    compiler/build/token_flowc.o \
    compiler/build/ast_flowc.o \
    compiler/build/lexer_flowc.o \
    compiler/build/parser_flowc.o \
    compiler/build/fileio_flowc.o \
    compiler/build/cgen_flowc.o \
    compiler/build/typecheck_flowc.o \
    compiler/build/resolve_flowc.o
for sym in flowc_make_tok flowc_ast_new flowc_lexer_next flowc_parse_program flowc_read_file flowc_cgen_emit flowc_typecheck flowc_tc_seed_export flowc_bundle_emit flowc_bundle_typecheck flowc_resolve_sibling_path; do
    if ! nm compiler/build/flowc_frontend.o | grep -q "$sym"; then
        echo "FAIL link smoke: ${sym} missing from flowc_frontend.o" >&2
        exit 1
    fi
done
echo "PASS link smoke flowc_frontend.o"

# Headers for the tiny C host (Parser / AstArena layouts from Stage-A emit).
python3 compiler/scripts/flowc_c_to_hdr.py \
    compiler/build/parser_flowc.c compiler/build/parser_flowc.h
python3 compiler/scripts/flowc_c_to_hdr.py \
    compiler/build/cgen_flowc.c compiler/build/cgen_flowc.h
python3 compiler/scripts/flowc_c_to_hdr.py \
    compiler/build/fileio_flowc.c compiler/build/fileio_flowc.h
python3 compiler/scripts/flowc_c_to_hdr.py \
    compiler/build/typecheck_flowc.c compiler/build/typecheck_flowc.h
python3 compiler/scripts/flowc_c_to_hdr.py \
    compiler/build/resolve_flowc.c compiler/build/resolve_flowc.h

# Stage-A driver: C main + flowc_frontend.o → parse/cgen fixture → exit 45.
echo "=== stage_a_driver ==="
cc -O0 -I compiler/build -I compiler/host \
    -o compiler/build/stage_a_driver \
    compiler/host/stage_a_driver.c \
    compiler/build/flowc_frontend.o
./compiler/build/stage_a_driver \
    compiler/fixtures/stage_a_sum.flow \
    compiler/build/driven_sum.c
cc -O0 -o compiler/build/driven_sum compiler/build/driven_sum.c
set +e
./compiler/build/driven_sum
driven_code=$?
set -e
echo "driven_sum exit=$driven_code"
test "$driven_code" -eq 45
echo "PASS stage_a_driver"

# Flow-written Stage-A driver: emit driver.flow (imports skipped) → link frontend.
# Prefers CLI argv; getenv FLOWC_IN / FLOWC_OUT kept for compatibility.
echo "=== stage_a_driver_flow ==="
compile_module driver compiler/src/driver.flow \
    compiler/build/token_flowc.h \
    compiler/build/ast_flowc.h \
    compiler/build/lexer_flowc.h \
    compiler/build/parser_flowc.h \
    compiler/build/fileio_flowc.h \
    compiler/build/cgen_flowc.h \
    compiler/build/typecheck_flowc.h \
    compiler/build/resolve_flowc.h
if ! grep -Fq 'int main(int argc, char **argv)' compiler/build/driver_flowc.c; then
    echo "FAIL stage_a_driver_flow: expected int main(int argc, char **argv) in emitted C" >&2
    exit 1
fi
# Imports skipped — parse/cgen bodies must not appear in the driver TU.
if grep -Eq '^int32_t flowc_parse_program' compiler/build/driver_flowc.c; then
    echo "FAIL stage_a_driver_flow: parse symbols must come from frontend, not driver emit" >&2
    exit 1
fi
cc -O0 -o compiler/build/stage_a_driver_flow \
    compiler/build/driver_flowc.o \
    compiler/build/flowc_frontend.o
# CLI path (preferred).
./compiler/build/stage_a_driver_flow \
    compiler/fixtures/stage_a_sum.flow \
    compiler/build/driven_sum_flow_cli.c
cc -O0 -o compiler/build/driven_sum_flow_cli compiler/build/driven_sum_flow_cli.c
set +e
./compiler/build/driven_sum_flow_cli
driven_flow_cli_code=$?
set -e
echo "driven_sum_flow_cli exit=$driven_flow_cli_code"
test "$driven_flow_cli_code" -eq 45
# getenv path (compat).
FLOWC_IN=compiler/fixtures/stage_a_sum.flow \
FLOWC_OUT=compiler/build/driven_sum_flow.c \
    ./compiler/build/stage_a_driver_flow
cc -O0 -o compiler/build/driven_sum_flow compiler/build/driven_sum_flow.c
set +e
./compiler/build/driven_sum_flow
driven_flow_code=$?
set -e
echo "driven_sum_flow exit=$driven_flow_code"
test "$driven_flow_code" -eq 45
echo "PASS stage_a_driver_flow"

# f32/f64 + float literals — after frontend rebuild so Stage-A driver can parse TOK_FLOAT.
run_case stage_a_float 42
if ! grep -Fq 'float x = 40.5f;' compiler/build/stage_a_float.c; then
    echo "FAIL stage_a_float: expected f32 let with 40.5f" >&2
    exit 1
fi
if ! grep -Fq 'double y = 1.5;' compiler/build/stage_a_float.c; then
    echo "FAIL stage_a_float: expected f64 let with 1.5" >&2
    exit 1
fi
if ! grep -Fq '(int32_t)(z)' compiler/build/stage_a_float.c; then
    echo "FAIL stage_a_float: expected cast to i32" >&2
    exit 1
fi

# Mini self-host: prefer Flow driver CLI when present (built above); C driver
# fallback. Ends with stage_a_driver_flow_self (Flow driver + self frontend).
./compiler/scripts/stage_a_self_emit.sh

# Gen2: driver linked against self.o re-emits frontend → flowc_frontend_g2.o,
# then fixed-point cmp self.o==g2.o, C/Flow g2 driver smokes (sum→45), gen3 token cmp.
./compiler/scripts/stage_a_self_emit_g2.sh

echo "ALL PASS"
