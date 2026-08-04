#!/usr/bin/env bash
# Mini self-host: Stage-A driver emits real frontend sources → C → .o → link.
# Requires compiler/build/stage_a_driver (run roundtrip.sh first, or build via it).
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
cd "$ROOT"
mkdir -p compiler/build

if [[ ! -x compiler/build/stage_a_driver ]]; then
    echo "FAIL stage_a_self_emit: missing compiler/build/stage_a_driver (run roundtrip.sh first)" >&2
    exit 1
fi

# Emit + compile one frontend module via the Stage-A driver binary.
# Optional further args: header paths for `cc -include` (imported sibling types/consts).
self_emit_module() {
    local name="$1"
    shift
    local src="compiler/src/${name}.flow"
    local c_out="compiler/build/self_${name}.c"
    local obj="compiler/build/self_${name}.o"
    local -a cc_args=(-O0 -c)

    echo "=== self_emit ${name} ==="
    ./compiler/build/stage_a_driver "$src" "$c_out"
    local h
    for h in "$@"; do
        cc_args+=(-include "$h")
    done
    cc "${cc_args[@]}" "$c_out" -o "$obj"
    echo "PASS self_emit ${name}"
}

# Order mirrors compile_module in roundtrip.sh (token → … → cgen).
self_emit_module token
python3 compiler/scripts/flowc_c_to_hdr.py \
    compiler/build/self_token.c compiler/build/self_token.h

self_emit_module ast

self_emit_module lexer compiler/build/self_token.h
python3 compiler/scripts/flowc_c_to_hdr.py \
    compiler/build/self_ast.c compiler/build/self_ast.h
python3 compiler/scripts/flowc_c_to_hdr.py \
    compiler/build/self_lexer.c compiler/build/self_lexer.h

self_emit_module fileio

self_emit_module parser \
    compiler/build/self_token.h \
    compiler/build/self_ast.h \
    compiler/build/self_lexer.h

self_emit_module cgen \
    compiler/build/self_token.h \
    compiler/build/self_ast.h

# Relocatable link: proves driver-emitted frontend objects resolve together.
cc -r -o compiler/build/flowc_frontend_self.o \
    compiler/build/self_token.o \
    compiler/build/self_ast.o \
    compiler/build/self_lexer.o \
    compiler/build/self_parser.o \
    compiler/build/self_fileio.o \
    compiler/build/self_cgen.o
for sym in flowc_make_tok flowc_ast_new flowc_lexer_next flowc_parse_program flowc_read_file flowc_cgen_emit; do
    if ! nm compiler/build/flowc_frontend_self.o | grep -q "$sym"; then
        echo "FAIL stage_a_self_emit: ${sym} missing from flowc_frontend_self.o" >&2
        exit 1
    fi
done
echo "PASS stage_a_self_emit flowc_frontend_self.o"
