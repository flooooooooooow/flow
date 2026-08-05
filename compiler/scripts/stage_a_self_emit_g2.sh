#!/usr/bin/env bash
# Gen2 mini self-host: link driver against flowc_frontend_self.o, then re-emit
# all eight frontend modules → g2_*.c / g2_*.o → flowc_frontend_g2.o.
# After link: cmp self.o==g2.o (fixed-point fail), stage_a_driver_g2 +
# stage_a_driver_flow_g2 smokes (sum→45), gen3 token emit cmp vs
# self_token.c / g2_token.c.
# Requires compiler/build/flowc_frontend_self.o (+ self_driver.o for the Flow
# g2 driver; run stage_a_self_emit.sh first).
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
cd "$ROOT"
mkdir -p compiler/build

if [[ ! -f compiler/build/flowc_frontend_self.o ]]; then
    echo "FAIL stage_a_self_emit_g2: missing compiler/build/flowc_frontend_self.o (run stage_a_self_emit.sh first)" >&2
    exit 1
fi

# Headers for the C host ABI (same layouts as host-emitted *_flowc.h).
for mod in token ast lexer parser cgen typecheck resolve; do
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
    # Frontend modules: imports/extern — opt out of default-on typecheck.
    FLOWC_TYPECHECK=0 ./compiler/build/stage_a_driver_self "$src" "$c_out"
    local h
    for h in "$@"; do
        cc_args+=(-include "$h")
    done
    cc "${cc_args[@]}" "$c_out" -o "$obj"
    echo "PASS g2_emit ${name}"
}

# Order mirrors stage_a_self_emit.sh (token → … → typecheck → resolve).
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

g2_emit_module typecheck \
    compiler/build/g2_ast.h

python3 compiler/scripts/flowc_c_to_hdr.py \
    compiler/build/g2_parser.c compiler/build/g2_parser.h
python3 compiler/scripts/flowc_c_to_hdr.py \
    compiler/build/g2_fileio.c compiler/build/g2_fileio.h
python3 compiler/scripts/flowc_c_to_hdr.py \
    compiler/build/g2_cgen.c compiler/build/g2_cgen.h
python3 compiler/scripts/flowc_c_to_hdr.py \
    compiler/build/g2_typecheck.c compiler/build/g2_typecheck.h

g2_emit_module resolve \
    compiler/build/g2_token.h \
    compiler/build/g2_ast.h \
    compiler/build/g2_lexer.h \
    compiler/build/g2_parser.h \
    compiler/build/g2_fileio.h \
    compiler/build/g2_cgen.h \
    compiler/build/g2_typecheck.h

# Relocatable link: proves driver_self-emitted frontend objects resolve together.
cc -r -o compiler/build/flowc_frontend_g2.o \
    compiler/build/g2_token.o \
    compiler/build/g2_ast.o \
    compiler/build/g2_lexer.o \
    compiler/build/g2_parser.o \
    compiler/build/g2_fileio.o \
    compiler/build/g2_cgen.o \
    compiler/build/g2_typecheck.o \
    compiler/build/g2_resolve.o
for sym in flowc_make_tok flowc_ast_new flowc_lexer_next flowc_parse_program flowc_read_file flowc_cgen_emit flowc_typecheck flowc_tc_seed_export flowc_bundle_emit flowc_bundle_typecheck flowc_resolve_sibling_path; do
    if ! nm compiler/build/flowc_frontend_g2.o | grep "$sym" >/dev/null; then
        echo "FAIL stage_a_self_emit_g2: ${sym} missing from flowc_frontend_g2.o" >&2
        exit 1
    fi
done

echo "=== self vs g2 object sizes ==="
wc -c compiler/build/flowc_frontend_self.o compiler/build/flowc_frontend_g2.o

# Fixed-point is semantic emit identity (C), not relocatable .o bytes —
# objects can differ from include-path / toolchain metadata while C matches.
echo "=== fixed-point cmp self_*.c vs g2_*.c ==="
fp_fail=0
for mod in token ast lexer fileio parser cgen typecheck resolve; do
    if ! cmp -s "compiler/build/self_${mod}.c" "compiler/build/g2_${mod}.c"; then
        echo "FAIL C drift: ${mod}" >&2
        diff -u "compiler/build/self_${mod}.c" "compiler/build/g2_${mod}.c" | head -80 >&2 || true
        fp_fail=1
    else
        echo "PASS C fixed-point: ${mod}"
    fi
done
if [[ "$fp_fail" -ne 0 ]]; then
    echo "FAIL stage_a_self_emit_g2: self/g2 C emit not fixed-point" >&2
    exit 1
fi
echo "PASS fixed-point self_*.c == g2_*.c"

if ! cmp -s compiler/build/flowc_frontend_self.o compiler/build/flowc_frontend_g2.o; then
    echo "WARN object bytes differ (self.o vs g2.o); C fixed-point still holds" >&2
else
    echo "PASS object bytes also match self.o == g2.o"
fi

# Gen2 driver: C host + flowc_frontend_g2.o → parse/cgen fixture → exit 45.
echo "=== stage_a_driver_g2 build ==="
cc -O0 -I compiler/build -I compiler/host \
    -o compiler/build/stage_a_driver_g2 \
    compiler/host/stage_a_driver.c \
    compiler/build/flowc_frontend_g2.o

echo "=== stage_a_driver_g2 smoke (stage_a_sum → exit 45) ==="
./compiler/build/stage_a_driver_g2 \
    compiler/fixtures/stage_a_sum.flow \
    compiler/build/driven_sum_g2.c
cc -O0 -o compiler/build/driven_sum_g2 compiler/build/driven_sum_g2.c
set +e
./compiler/build/driven_sum_g2
driven_g2_code=$?
set -e
echo "driven_sum_g2 exit=$driven_g2_code"
test "$driven_g2_code" -eq 45
echo "PASS stage_a_driver_g2"

# Flow driver + g2 frontend: same Stage-A-emitted self_driver.o linked against
# flowc_frontend_g2.o (fully Flow-emitted driver + gen2 frontend).
if [[ ! -f compiler/build/self_driver.o ]]; then
    echo "FAIL stage_a_driver_flow_g2: missing compiler/build/self_driver.o (run stage_a_self_emit.sh first)" >&2
    exit 1
fi
echo "=== stage_a_driver_flow_g2 build ==="
cc -O0 -o compiler/build/stage_a_driver_flow_g2 \
    compiler/build/self_driver.o \
    compiler/build/flowc_frontend_g2.o
echo "=== stage_a_driver_flow_g2 smoke (stage_a_sum → exit 45) ==="
./compiler/build/stage_a_driver_flow_g2 \
    compiler/fixtures/stage_a_sum.flow \
    compiler/build/driven_sum_flow_g2.c
cc -O0 -o compiler/build/driven_sum_flow_g2 compiler/build/driven_sum_flow_g2.c
set +e
./compiler/build/driven_sum_flow_g2
driven_flow_g2_code=$?
set -e
echo "driven_sum_flow_g2 exit=$driven_flow_g2_code"
test "$driven_flow_g2_code" -eq 45
echo "PASS stage_a_driver_flow_g2"

# Gen3 probe: driver_g2 re-emits token; must match self/g2 token C (deterministic).
echo "=== gen3 token emit (driver_g2) ==="
FLOWC_TYPECHECK=0 ./compiler/build/stage_a_driver_g2 \
    compiler/src/token.flow \
    compiler/build/gen3_token.c
if ! cmp -s compiler/build/gen3_token.c compiler/build/g2_token.c; then
    echo "FAIL stage_a_self_emit_g2: gen3_token.c != g2_token.c" >&2
    exit 1
fi
if ! cmp -s compiler/build/gen3_token.c compiler/build/self_token.c; then
    echo "FAIL stage_a_self_emit_g2: gen3_token.c != self_token.c" >&2
    exit 1
fi
echo "PASS gen3 token == g2_token == self_token"

echo "PASS stage_a_self_emit_g2 flowc_frontend_g2.o"
