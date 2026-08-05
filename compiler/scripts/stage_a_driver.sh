#!/usr/bin/env bash
# Build + smoke the Stage-A C driver against flowc_frontend.o.
# Prefer running via roundtrip.sh (which builds the .o first); this script
# assumes compiler/build/flowc_frontend.o and sibling *_flowc.h already exist.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
cd "$ROOT"
mkdir -p compiler/build

if [[ ! -f compiler/build/flowc_frontend.o ]]; then
    echo "FAIL stage_a_driver: missing compiler/build/flowc_frontend.o (run roundtrip.sh first)" >&2
    exit 1
fi

# Ensure generated headers exist (parser/cgen may not have been hdr'd yet).
for mod in token ast lexer parser cgen typecheck resolve; do
    if [[ ! -f "compiler/build/${mod}_flowc.h" ]]; then
        if [[ ! -f "compiler/build/${mod}_flowc.c" ]]; then
            echo "FAIL stage_a_driver: missing compiler/build/${mod}_flowc.c" >&2
            exit 1
        fi
        python3 compiler/scripts/flowc_c_to_hdr.py \
            "compiler/build/${mod}_flowc.c" "compiler/build/${mod}_flowc.h"
    fi
done

echo "=== stage_a_driver build ==="
cc -O0 -I compiler/build -I compiler/host \
    -o compiler/build/stage_a_driver \
    compiler/host/stage_a_driver.c \
    compiler/build/flowc_frontend.o

echo "=== stage_a_driver smoke (stage_a_sum → exit 45) ==="
./compiler/build/stage_a_driver \
    compiler/fixtures/stage_a_sum.flow \
    compiler/build/driven_sum.c
cc -O0 -o compiler/build/driven_sum compiler/build/driven_sum.c
set +e
./compiler/build/driven_sum
code=$?
set -e
echo "driven_sum exit=$code"
test "$code" -eq 45
echo "PASS stage_a_driver"
