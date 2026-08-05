#!/usr/bin/env bash
# First-slice import-aware Stage-A: emit two Flow files → cc → exit 42.
#
# Practical path (no recursive resolve yet):
#   - Emit math.flow and main.flow separately (main's `import .math` skipped)
#   - export function add → non-static C symbol
#   - Link both .o → binary returns add(40, 2) == 42
#
# Optional: FLOWC_RESOLVE_IMPORTS=1 also lists sibling paths resolved from
# `import .name` in main (documentation / future driver hook); emit still
# walks the package dir for this fixture.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
cd "$ROOT"
mkdir -p compiler/build/pkg_add
export FLOW_HOST=python

PKG="compiler/fixtures/pkg_add"
BUILD="compiler/build/pkg_add"

emit_one() {
    local src="$1"
    local c_out="$2"
    # Prefer Stage-A Flow driver when built (dogfood); else Python host bootstrap.
    # Typecheck on: `import .math { add }` seeds the name for main.flow.
    if [[ -x compiler/build/stage_a_driver_flow ]]; then
        ./compiler/build/stage_a_driver_flow "$src" "$c_out"
    else
        export FLOWC_IN="$src"
        export FLOWC_OUT="$c_out"
        ./flow run compiler/src/main.flow
    fi
}

echo "=== stage_a_link_two (pkg_add) ==="

emit_one "$PKG/math.flow" "$BUILD/math.c"
emit_one "$PKG/main.flow" "$BUILD/main.c"

# export function must be a linkable (non-static) C symbol.
if ! grep -Eq '^int32_t add\(' "$BUILD/math.c"; then
    echo "FAIL stage_a_link_two: expected non-static int32_t add(...) in math.c" >&2
    exit 1
fi
if grep -Eq '^static int32_t add\(' "$BUILD/math.c"; then
    echo "FAIL stage_a_link_two: export add must not be static" >&2
    exit 1
fi

# Import skipped — main still calls add by free name.
if ! grep -Fq 'add(40, 2)' "$BUILD/main.c"; then
    echo "FAIL stage_a_link_two: expected add(40, 2) call in main.c" >&2
    exit 1
fi
# No duplicate add body in main TU.
if grep -Eq '^int32_t add\(' "$BUILD/main.c"; then
    echo "FAIL stage_a_link_two: add must come from math.o, not main emit" >&2
    exit 1
fi

if [[ "${FLOWC_RESOLVE_IMPORTS:-}" == "1" ]]; then
    # Resolve `import .sibling` from main → same-dir sibling .flow (smoke for
    # future driver recursion). Fixture expects .math → math.flow.
    main_src="$(cat "$PKG/main.flow")"
    if [[ "$main_src" =~ import[[:space:]]+\.([A-Za-z_][A-Za-z0-9_]*) ]]; then
        sib="${BASH_REMATCH[1]}"
        sib_path="$PKG/${sib}.flow"
        if [[ ! -f "$sib_path" ]]; then
            echo "FAIL stage_a_link_two: FLOWC_RESOLVE_IMPORTS resolved missing $sib_path" >&2
            exit 1
        fi
        echo "resolve_import .${sib} -> ${sib_path}"
    else
        echo "FAIL stage_a_link_two: FLOWC_RESOLVE_IMPORTS=1 but no import .sibling in main" >&2
        exit 1
    fi
fi

cc -O0 -c "$BUILD/math.c" -o "$BUILD/math.o"
# Prototype for imported `add` (imports skipped at emit — supply via sibling header).
python3 compiler/scripts/flowc_c_to_hdr.py "$BUILD/math.c" "$BUILD/math.h"
cc -O0 -c -include "$BUILD/math.h" "$BUILD/main.c" -o "$BUILD/main.o"
cc -O0 -o "$BUILD/pkg_add" "$BUILD/main.o" "$BUILD/math.o"

set +e
"$BUILD/pkg_add"
code=$?
set -e
echo "pkg_add exit=$code"
test "$code" -eq 42
echo "PASS stage_a_link_two"
