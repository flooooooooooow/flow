#!/usr/bin/env bash
# Stage-A flowc emit → clang → run for each fixture; check expected exit codes.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
cd "$ROOT"
mkdir -p compiler/build
# Gen0 bootstrap + dogfood of compiler/src via ./flow always uses the Python host.
# (Default FLOW_HOST=flowc is for user Stage-A programs after a driver exists.)
export FLOW_HOST=python

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
# Typecheck stays on (default); imports seed names so frontend modules resolve.
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
    FLOWC_FORCE_HOST=1 stage_a_emit "$src" "$c_out"
    local h
    for h in "$@"; do
        cc_args+=(-include "$h")
    done
    cc "${cc_args[@]}" "$c_out" -o "$obj"
    echo "PASS compile_module ${name}"
}

run_case stage_a_sum 45
run_case stage_a_for_sum 45
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
# Inferred `let` (no `: Type`): struct-returning call, cast, struct literal.
run_case stage_a_infer_struct 42
if ! grep -Fq 'Pair p = make_pair(20, 22);' compiler/build/stage_a_infer_struct.c; then
    echo "FAIL stage_a_infer_struct: inferred let should be typed Pair" >&2
    grep -n 'make_pair(20' compiler/build/stage_a_infer_struct.c >&2 || true
    exit 1
fi
if grep -Fq 'int32_t p = make_pair' compiler/build/stage_a_infer_struct.c; then
    echo "FAIL stage_a_infer_struct: struct return inferred as int32_t" >&2
    exit 1
fi
if ! grep -Fq 'int64_t wide = (int64_t)(7);' compiler/build/stage_a_infer_struct.c; then
    echo "FAIL stage_a_infer_struct: cast init should infer int64_t" >&2
    exit 1
fi
if ! grep -Fq 'Pair lit = (Pair){' compiler/build/stage_a_infer_struct.c; then
    echo "FAIL stage_a_infer_struct: struct literal init should infer Pair" >&2
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
if ! nm compiler/build/lexer_flowc.o | grep 'flowc_lexer_next' >/dev/null; then
    echo "FAIL compile_module lexer: flowc_lexer_next missing from object" >&2
    exit 1
fi
if ! nm compiler/build/token_flowc.o | grep 'TOK_EOF' >/dev/null; then
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
    if ! nm compiler/build/flowc_jsgen_fmt.o | grep "$sym" >/dev/null; then
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

# Phase A's stable bootstrap boundary ends here. The remaining bundle,
# typecheck, self-emit, and fixed-point checks exercise Phase B work and may be
# enabled independently while those gaps are being closed.
if [[ "${FLOWC_PHASE_A_ONLY:-}" == "1" ]]; then
    echo "PASS flowc Phase-A roundtrip"
    exit 0
fi

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
# bundle_infer_main: `let p = make_pair(...)` where make_pair lives in the
# sibling module — the type has to come from the bundle signature table.
FLOWC_FORCE_HOST=1 FLOWC_BUNDLE=1 FLOWC_DIR=compiler/fixtures \
    stage_a_emit \
    compiler/fixtures/bundle_infer_main.flow \
    compiler/build/bundle_infer_main.c
if ! grep -Fq 'Pair p = make_pair(20, 22);' compiler/build/bundle_infer_main.c; then
    echo "FAIL bundle_infer: cross-module inferred let should be typed Pair" >&2
    grep -n 'make_pair(20' compiler/build/bundle_infer_main.c >&2 || true
    exit 1
fi
if grep -Fq 'int32_t p = make_pair' compiler/build/bundle_infer_main.c; then
    echo "FAIL bundle_infer: cross-module struct return inferred as int32_t" >&2
    exit 1
fi
cc -O0 -o compiler/build/bundle_infer_main compiler/build/bundle_infer_main.c
set +e
./compiler/build/bundle_infer_main
bundle_infer_code=$?
set -e
echo "bundle_infer_main exit=$bundle_infer_code"
test "$bundle_infer_code" -eq 42

echo "PASS FLOWC_BUNDLE fixtures"

# Real frontend pair: FLOWC_BUNDLE=1 emits token.flow then lexer.flow in one TU
# (deps first). No flowc_c_to_hdr.py / cc -include — Token/TOK_* live in the same file.
echo "=== FLOWC_BUNDLE lexer (token+lexer one TU) ==="
FLOWC_FORCE_HOST=1 FLOWC_BUNDLE=1 FLOWC_DIR=compiler/src \
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
if ! nm compiler/build/bundle_lexer.o | grep 'flowc_lexer_next' >/dev/null; then
    echo "FAIL FLOWC_BUNDLE lexer: flowc_lexer_next missing from object" >&2
    exit 1
fi
if ! nm compiler/build/bundle_lexer.o | grep 'TOK_EOF' >/dev/null; then
    echo "FAIL FLOWC_BUNDLE lexer: TOK_EOF missing from object" >&2
    exit 1
fi
echo "PASS FLOWC_BUNDLE lexer (token+lexer one TU)"

# Frontend parser bundle: FLOWC_BUNDLE=1 emits token+ast+lexer+parser in one TU
# (deps first). Needs 1MB out_cap in main/driver. No flowc_c_to_hdr.py / -include.
echo "=== FLOWC_BUNDLE parser (token+ast+lexer+parser one TU) ==="
FLOWC_FORCE_HOST=1 FLOWC_BUNDLE=1 FLOWC_DIR=compiler/src \
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
if ! nm compiler/build/bundle_parser.o | grep 'flowc_parse_program' >/dev/null; then
    echo "FAIL FLOWC_BUNDLE parser: flowc_parse_program missing from object" >&2
    exit 1
fi
if ! nm compiler/build/bundle_parser.o | grep 'flowc_lexer_next' >/dev/null; then
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
    compiler/build/typecheck_undef.c \
    >compiler/build/typecheck_undef.log 2>&1
tc_bad_rc=$?
set -e
echo "typecheck_undef emit rc=$tc_bad_rc"
test "$tc_bad_rc" -ne 0
if [[ -f compiler/build/typecheck_undef.c ]]; then
    echo "FAIL FLOWC_TYPECHECK: undef fixture should not write C" >&2
    exit 1
fi
if ! grep -Fq 'flowc tc: unbound ident' compiler/build/typecheck_undef.log; then
    echo "FAIL FLOWC_TYPECHECK: expected unbound ident diagnostic" >&2
    cat compiler/build/typecheck_undef.log >&2
    exit 1
fi
# `return y` is on line 5 of typecheck_undef.flow (1-based).
if ! grep -Eq 'flowc tc: at 5:' compiler/build/typecheck_undef.log; then
    echo "FAIL FLOWC_TYPECHECK: expected location-rich diagnostic (at 5:…)" >&2
    cat compiler/build/typecheck_undef.log >&2
    exit 1
fi
if ! grep -Fq 'compiler/fixtures/typecheck_undef.flow' compiler/build/typecheck_undef.log; then
    echo "FAIL FLOWC_TYPECHECK: expected file path in diagnostic" >&2
    cat compiler/build/typecheck_undef.log >&2
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
    if ! nm compiler/build/flowc_frontend.o | grep "$sym" >/dev/null; then
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

# match statement — after frontend rebuild so the Stage-A driver can parse it.
# Arms: int literals (incl. negative), `_` wildcard, binding ident catch-all.
run_case stage_a_match 42
if ! grep -Fq 'int32_t __flowc_match = v;' compiler/build/stage_a_match.c; then
    echo "FAIL stage_a_match: expected scrutinee temp __flowc_match" >&2
    exit 1
fi
if ! grep -Fq '} else if (__flowc_match == -1) {' compiler/build/stage_a_match.c; then
    echo "FAIL stage_a_match: expected else-if chain with negative literal" >&2
    exit 1
fi
if ! grep -Fq 'int32_t other = __flowc_match;' compiler/build/stage_a_match.c; then
    echo "FAIL stage_a_match: expected binding arm decl" >&2
    exit 1
fi
# Unsupported pattern forms (struct patterns) must be rejected with a message.
rm -f compiler/build/match_unsupported.c
set +e
FLOWC_FORCE_HOST=1 stage_a_emit \
    compiler/fixtures/match_unsupported.flow \
    compiler/build/match_unsupported.c \
    >compiler/build/match_unsupported.log 2>&1
match_bad_rc=$?
set -e
echo "match_unsupported emit rc=$match_bad_rc"
test "$match_bad_rc" -ne 0
if [[ -f compiler/build/match_unsupported.c ]]; then
    echo "FAIL stage_a_match: unsupported-pattern fixture should not write C" >&2
    exit 1
fi
if ! grep -Fq 'struct patterns not supported in Stage-A match' compiler/build/match_unsupported.log; then
    echo "FAIL stage_a_match: expected unsupported-pattern diagnostic" >&2
    cat compiler/build/match_unsupported.log >&2
    exit 1
fi
echo "PASS stage_a_match fixtures"

# Mini self-host: prefer Flow driver CLI when present (built above); C driver
# fallback. Ends with stage_a_driver_flow_self (Flow driver + self frontend).
./compiler/scripts/stage_a_self_emit.sh

# Gen2: driver linked against self.o re-emits frontend → flowc_frontend_g2.o,
# then fixed-point cmp self.o==g2.o, C/Flow g2 driver smokes (sum→45), gen3 token cmp.
./compiler/scripts/stage_a_self_emit_g2.sh

# Checked-in bootstrap: a cc-only path to a working flowc, and the C in
# compiler/bootstrap/ must still be exactly what flowc emits from compiler/src.
./compiler/scripts/bootstrap_from_c.sh --verify

# Whole-compiler self-host: bundle all of compiler/src through flowc, run its
# self-tests, and check three consecutive generations are byte-identical.
./compiler/scripts/self_host_full.sh

echo "ALL PASS"
