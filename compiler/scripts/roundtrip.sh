#!/usr/bin/env bash
# Stage-A flowc emit → clang → run for each fixture; check expected exit codes.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
cd "$ROOT"
mkdir -p compiler/build

run_case() {
    local name="$1"
    local expect="$2"
    local fixture="compiler/fixtures/${name}.flow"
    local c_out="compiler/build/${name}.c"
    local bin="compiler/build/${name}"

    echo "=== ${name} ==="
    export FLOWC_IN="$fixture"
    export FLOWC_OUT="$c_out"
    ./flow run compiler/src/main.flow
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
compile_module() {
    local name="$1"
    local src="$2"
    shift 2
    local c_out="compiler/build/${name}_flowc.c"
    local obj="compiler/build/${name}_flowc.o"
    local -a cc_args=(-O0 -c)

    echo "=== compile_module ${name} ==="
    export FLOWC_IN="$src"
    export FLOWC_OUT="$c_out"
    ./flow run compiler/src/main.flow
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
# Dogfood: Token struct + flowc_make_tok (struct return type).
run_case stage_a_token_struct 26
# ptr<i32> params/lets + unary & + index (exit 40+2).
run_case stage_a_ptr 42
# expr as Type casts (exit 42).
run_case stage_a_cast 42
# indexed assign p[0] = n (exit 42).
run_case stage_a_index_assign 42

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
for needle in 'flowc_cgen_emit' 'typedef struct CgenBuf' '#include <string.h>' ' % '; do
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

# Link smoke: all frontend modules resolve into one relocatable object.
cc -r -o compiler/build/flowc_frontend.o \
    compiler/build/token_flowc.o \
    compiler/build/ast_flowc.o \
    compiler/build/lexer_flowc.o \
    compiler/build/parser_flowc.o \
    compiler/build/fileio_flowc.o \
    compiler/build/cgen_flowc.o
for sym in flowc_make_tok flowc_ast_new flowc_lexer_next flowc_parse_program flowc_read_file flowc_cgen_emit; do
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
# getenv FLOWC_IN / FLOWC_OUT (host Flow main has no argv; Stage-A same).
echo "=== stage_a_driver_flow ==="
compile_module driver compiler/src/driver.flow \
    compiler/build/token_flowc.h \
    compiler/build/ast_flowc.h \
    compiler/build/lexer_flowc.h \
    compiler/build/parser_flowc.h \
    compiler/build/fileio_flowc.h \
    compiler/build/cgen_flowc.h
if ! grep -Fq 'int32_t main(' compiler/build/driver_flowc.c; then
    echo "FAIL stage_a_driver_flow: expected int32_t main() in emitted C" >&2
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

# Mini self-host: driver emits real frontend sources → C → .o → link.
./compiler/scripts/stage_a_self_emit.sh

# Gen2: driver linked against self.o re-emits frontend → flowc_frontend_g2.o.
./compiler/scripts/stage_a_self_emit_g2.sh

echo "ALL PASS"
