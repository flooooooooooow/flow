#!/usr/bin/env bash
# Gen2 mini self-host: link driver against flowc_frontend_self.o, then re-emit
# all six frontend modules → g2_*.c / g2_*.o → flowc_frontend_g2.o.
# Requires compiler/build/flowc_frontend_self.o (run stage_a_self_emit.sh first).
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
cd "$ROOT"
mkdir -p compiler/build

if [[ ! -f compiler/build/flowc_frontend_self.o ]]; then
    echo "FAIL stage_a_self_emit_g2: missing compiler/build/flowc_frontend_self.o (run stage_a_self_emit.sh first)" >&2
    exit 1
fi

# Headers for the C host ABI (same layouts as host-emitted *_flowc.h).
for mod in token ast lexer parser cgen; do
    if [[ ! -f "compiler/build/${mod}_flowc.h" ]]; then
        if [[ ! -f "compiler/build/${mod}_flowc.c" ]]; then
            echo "FAIL stage_a_self_emit_g2: missing compiler/build/${mod}_flowc.c" >&2
            exit 1
        fi
        python3 compiler/scripts/flowc_c_to_hdr.py \
            "compiler/build/${mod}_flowc.c" "compiler/build/${mod}_flowc.h"
    fi
done

echo "=== stage_a_driver_self build ==="
cc -O0 -I compiler/build -I compiler/host \
    -o compiler/build/stage_a_driver_self \
    compiler/host/stage_a_driver.c \
    compiler/build/flowc_frontend_self.o

# Smoke: self.o-backed driver on stage_a_sum → exit 45.
echo "=== stage_a_driver_self smoke (stage_a_sum → exit 45) ==="
./compiler/build/stage_a_driver_self \
    compiler/fixtures/stage_a_sum.flow \
    compiler/build/driven_sum_self.c
cc -O0 -o compiler/build/driven_sum_self compiler/build/driven_sum_self.c
set +e
./compiler/build/driven_sum_self
driven_self_code=$?
set -e
echo "driven_sum_self exit=$driven_self_code"
test "$driven_self_code" -eq 45
echo "PASS stage_a_driver_self"

# Emit + compile one frontend module via stage_a_driver_self.
# Optional further args: header paths for `cc -include` (imported sibling types/consts).
g2_emit_module() {
    local name="$1"
    shift
    local src="compiler/src/${name}.flow"
    local c_out="compiler/build/g2_${name}.c"
    local obj="compiler/build/g2_${name}.o"
    local -a cc_args=(-O0 -c)

    echo "=== g2_emit ${name} ==="
    ./compiler/build/stage_a_driver_self "$src" "$c_out"
    local h
    for h in "$@"; do
        cc_args+=(-include "$h")
    done
    cc "${cc_args[@]}" "$c_out" -o "$obj"
    echo "PASS g2_emit ${name}"
}

# Order mirrors stage_a_self_emit.sh (token → … → cgen).
# Headers: g2_* siblings (same role as self_* in gen1).
g2_emit_module token
python3 compiler/scripts/flowc_c_to_hdr.py \
    compiler/build/g2_token.c compiler/build/g2_token.h

g2_emit_module ast

g2_emit_module lexer compiler/build/g2_token.h
python3 compiler/scripts/flowc_c_to_hdr.py \
    compiler/build/g2_ast.c compiler/build/g2_ast.h
python3 compiler/scripts/flowc_c_to_hdr.py \
    compiler/build/g2_lexer.c compiler/build/g2_lexer.h

g2_emit_module fileio

g2_emit_module parser \
    compiler/build/g2_token.h \
    compiler/build/g2_ast.h \
    compiler/build/g2_lexer.h

g2_emit_module cgen \
    compiler/build/g2_token.h \
    compiler/build/g2_ast.h

# Relocatable link: proves driver_self-emitted frontend objects resolve together.
cc -r -o compiler/build/flowc_frontend_g2.o \
    compiler/build/g2_token.o \
    compiler/build/g2_ast.o \
    compiler/build/g2_lexer.o \
    compiler/build/g2_parser.o \
    compiler/build/g2_fileio.o \
    compiler/build/g2_cgen.o
for sym in flowc_make_tok flowc_ast_new flowc_lexer_next flowc_parse_program flowc_read_file flowc_cgen_emit; do
    if ! nm compiler/build/flowc_frontend_g2.o | grep -q "$sym"; then
        echo "FAIL stage_a_self_emit_g2: ${sym} missing from flowc_frontend_g2.o" >&2
        exit 1
    fi
done

echo "=== self vs g2 object sizes ==="
wc -c compiler/build/flowc_frontend_self.o compiler/build/flowc_frontend_g2.o
echo "PASS stage_a_self_emit_g2 flowc_frontend_g2.o"
