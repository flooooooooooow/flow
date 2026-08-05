#!/usr/bin/env bash
# Mini self-host: Stage-A driver emits real frontend sources → C → .o → link,
# then emits driver.flow → self_driver.o and links stage_a_driver_flow_self
# (Stage-A Flow driver + self frontend). Prefers stage_a_driver_flow (CLI)
# when present; falls back to C stage_a_driver.
# Requires one of those binaries (run roundtrip.sh first, or build via it).
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
cd "$ROOT"
mkdir -p compiler/build

STAGE_A_DRIVER=""
if [[ -x compiler/build/stage_a_driver_flow ]]; then
    STAGE_A_DRIVER=compiler/build/stage_a_driver_flow
elif [[ -x compiler/build/stage_a_driver ]]; then
    STAGE_A_DRIVER=compiler/build/stage_a_driver
else
    echo "FAIL stage_a_self_emit: missing stage_a_driver_flow or stage_a_driver (run roundtrip.sh first)" >&2
    exit 1
fi
echo "stage_a_self_emit: using ${STAGE_A_DRIVER}"

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
    # Frontend modules: imports/extern — opt out of default-on typecheck.
    FLOWC_TYPECHECK=0 "./${STAGE_A_DRIVER}" "$src" "$c_out"
    local h
    for h in "$@"; do
        cc_args+=(-include "$h")
    done
    cc "${cc_args[@]}" "$c_out" -o "$obj"
    echo "PASS self_emit ${name}"
}

# Order mirrors compile_module in roundtrip.sh (token → … → typecheck → resolve).
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

self_emit_module typecheck \
    compiler/build/self_ast.h

python3 compiler/scripts/flowc_c_to_hdr.py \
    compiler/build/self_parser.c compiler/build/self_parser.h
python3 compiler/scripts/flowc_c_to_hdr.py \
    compiler/build/self_fileio.c compiler/build/self_fileio.h
python3 compiler/scripts/flowc_c_to_hdr.py \
    compiler/build/self_cgen.c compiler/build/self_cgen.h

self_emit_module resolve \
    compiler/build/self_token.h \
    compiler/build/self_ast.h \
    compiler/build/self_lexer.h \
    compiler/build/self_parser.h \
    compiler/build/self_fileio.h \
    compiler/build/self_cgen.h

# Relocatable link: proves driver-emitted frontend objects resolve together.
cc -r -o compiler/build/flowc_frontend_self.o \
    compiler/build/self_token.o \
    compiler/build/self_ast.o \
    compiler/build/self_lexer.o \
    compiler/build/self_parser.o \
    compiler/build/self_fileio.o \
    compiler/build/self_cgen.o \
    compiler/build/self_typecheck.o \
    compiler/build/self_resolve.o
for sym in flowc_make_tok flowc_ast_new flowc_lexer_next flowc_parse_program flowc_read_file flowc_cgen_emit flowc_typecheck flowc_tc_seed_export flowc_bundle_emit flowc_bundle_typecheck flowc_resolve_sibling_path; do
    if ! nm compiler/build/flowc_frontend_self.o | grep "$sym" >/dev/null; then
        echo "FAIL stage_a_self_emit: ${sym} missing from flowc_frontend_self.o" >&2
        exit 1
    fi
done
# Frontend must not define main (that belongs to the Flow driver TU).
if nm compiler/build/flowc_frontend_self.o | grep -Eq '[[:space:]]T[[:space:]]+_?main$'; then
    echo "FAIL stage_a_self_emit: flowc_frontend_self.o must not define main" >&2
    exit 1
fi
echo "PASS stage_a_self_emit flowc_frontend_self.o"

# Fully Stage-A-bootstrapped Flow driver: emit driver.flow → self_driver.c,
# compile with self_* headers (Parser / fileio / cgen types), link against
# flowc_frontend_self.o. Only libc + cc remain outside the Flow emit path.
echo "=== stage_a_driver_flow_self build ==="
python3 compiler/scripts/flowc_c_to_hdr.py \
    compiler/build/self_typecheck.c compiler/build/self_typecheck.h
python3 compiler/scripts/flowc_c_to_hdr.py \
    compiler/build/self_resolve.c compiler/build/self_resolve.h

FLOWC_TYPECHECK=0 "./${STAGE_A_DRIVER}" \
    compiler/src/driver.flow \
    compiler/build/self_driver.c
if ! grep -Fq 'int main(int argc, char **argv)' compiler/build/self_driver.c; then
    echo "FAIL stage_a_driver_flow_self: expected int main(int argc, char **argv) in self_driver.c" >&2
    exit 1
fi
# Imports skipped — parse/cgen bodies must not appear in the driver TU.
if grep -Eq '^int32_t flowc_parse_program' compiler/build/self_driver.c; then
    echo "FAIL stage_a_driver_flow_self: parse symbols must come from frontend, not driver emit" >&2
    exit 1
fi
cc -O0 -c \
    -include compiler/build/self_token.h \
    -include compiler/build/self_ast.h \
    -include compiler/build/self_lexer.h \
    -include compiler/build/self_parser.h \
    -include compiler/build/self_fileio.h \
    -include compiler/build/self_cgen.h \
    -include compiler/build/self_typecheck.h \
    -include compiler/build/self_resolve.h \
    compiler/build/self_driver.c -o compiler/build/self_driver.o
cc -O0 -o compiler/build/stage_a_driver_flow_self \
    compiler/build/self_driver.o \
    compiler/build/flowc_frontend_self.o

echo "=== stage_a_driver_flow_self smoke (stage_a_sum → exit 45) ==="
./compiler/build/stage_a_driver_flow_self \
    compiler/fixtures/stage_a_sum.flow \
    compiler/build/driven_sum_flow_self.c
cc -O0 -o compiler/build/driven_sum_flow_self compiler/build/driven_sum_flow_self.c
set +e
./compiler/build/driven_sum_flow_self
driven_flow_self_code=$?
set -e
echo "driven_sum_flow_self exit=$driven_flow_self_code"
test "$driven_flow_self_code" -eq 45
echo "PASS stage_a_driver_flow_self"
