#!/usr/bin/env bash
# A user-defined function named like a math intrinsic is called as written,
# instead of lowering to the math dialect. Regression test for #874.
source "$(dirname "$0")/lib.sh"

check_math_intrinsic_override() {
    t_need mlir-opt mlir-translate clang
    cat > "$T_TMP/math_override.flow" <<'FLOW'

function exp(x: f32) -> f32 {
    return 42.0;
}

function main() -> i32 {
    let result = exp(0.0);
    if result == 42.0 {
        return 0;
    }
    return 1;
}
FLOW
    t_run ./flow run "$T_TMP/math_override.flow" --backend=c --json
    if [[ "$T_RC" -ne 0 ]]; then
        echo "C backend failed math override test"
        cat "$T_OUT" "$T_ERR"
        return 1
    fi
    t_run ./flow run "$T_TMP/math_override.flow" --backend=mlir --json
    if [[ "$T_RC" -ne 0 ]]; then
        echo "MLIR backend failed math override test"
        cat "$T_OUT" "$T_ERR"
        return 1
    fi
}

t_check math_intrinsic_override check_math_intrinsic_override
t_done
