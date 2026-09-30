#!/usr/bin/env bash
# Run the mlir-opt optimization pipeline that `flow mlir --optimize` selects.
#
#   compiler/scripts/mlir_optimize.sh [FLAGS] [--opt-report] IN.mlir OUT.mlir
#   compiler/scripts/mlir_optimize.sh --print-pass-pipeline [FLAGS]
#
# FLAGS: --opt-level O0|O1|O2|O3 (default O2), --no-vectorization,
# --loop-fusion, --no-mem2reg, --no-sccp, --no-licm, --no-cse, --no-dce,
# --no-inline, --enable-loop-pipelining, --enable-multi-buffering. Unknown
# flags are ignored, so callers can pass their whole flag list.
#
# The pass list comes from the Flow tool scripts/tools/mlir_pipeline; this
# script is the process half of the retired src/flow/mlir_optimizer.py:
# probe that mlir-opt parses the func/arith mix (an mlir-opt without the
# func dialect, as some Ubuntu mlir-14 packages ship, copies IN to OUT
# unchanged), run the pipeline, and with --opt-report write the pass
# statistics report to stderr.
#
# Exit status: mlir-opt's, 2 for bad arguments, 3 when mlir-opt is missing.
set -uo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd -P)"

print_only=0
report=0
flags=()
files=()
while [[ $# -gt 0 ]]; do
    case "$1" in
        --print-pass-pipeline) print_only=1 ;;
        --opt-report) report=1 ;;
        --opt-level) flags+=("$1" "${2:-}"); shift ;;
        -*) flags+=("$1") ;;
        *) files+=("$1") ;;
    esac
    shift
done

tool="$("$ROOT/scripts/tools/build_tool.sh" mlir_pipeline)" || {
    echo "mlir_optimize: could not build scripts/tools/mlir_pipeline" >&2
    exit 1
}
[[ "$tool" == /* ]] || tool="$ROOT/$tool"
pipeline="$("$tool" ${flags[@]+"${flags[@]}"})" || exit $?

if [[ "$print_only" -eq 1 ]]; then
    printf '%s\n' "$pipeline"
    exit 0
fi
if [[ ${#files[@]} -ne 2 ]]; then
    echo "usage: $0 [FLAGS] [--opt-report] IN.mlir OUT.mlir" >&2
    exit 2
fi
in="${files[0]}"
out="${files[1]}"

opt="$("$ROOT/compiler/scripts/mlir_lower.sh" --tools 2>/dev/null | sed -n 's/^mlir-opt=//p')"
if [[ -z "$opt" ]]; then
    echo "mlir_optimize: mlir-opt not found (brew install llvm, or set LLVM_PATH)" >&2
    exit 3
fi

copy_through() {
    [[ "$in" -ef "$out" ]] || cp "$in" "$out"
}

work="$(mktemp -d "${TMPDIR:-/tmp}/flow-mlir-opt.XXXXXX")"
trap 'rm -rf "$work"' EXIT

cat > "$work/probe.mlir" <<'EOF'
module {
  func.func @__flow_opt_probe(%arg0: i32) -> i32 {
    %0 = arith.constant 0 : i32
    func.return %0 : i32
  }
}
EOF
if ! "$opt" --mlir-print-op-on-diagnostic=false \
    "--pass-pipeline=builtin.module(func.func(canonicalize))" \
    "$work/probe.mlir" -o "$work/probe.out" </dev/null >/dev/null 2>&1; then
    copy_through
    exit 0
fi

rc=0
"$opt" --mlir-print-op-on-diagnostic=false "--pass-pipeline=$pipeline" \
    "$in" -o "$work/out.mlir" </dev/null 2>"$work/err" || rc=$?
if [[ "$rc" -ne 0 ]]; then
    if grep -q 'func.func' "$work/err" && grep -q 'unknown' "$work/err"; then
        copy_through
        exit 0
    fi
    echo "MLIR optimization failed: $(cat "$work/err")" >&2
    exit "$rc"
fi
cp "$work/out.mlir" "$out"

if [[ "$report" -eq 1 ]]; then
    cp "$out" "$work/report_in.mlir"
    "$opt" --mlir-print-op-on-diagnostic=false --mlir-pass-statistics \
        "--pass-pipeline=$pipeline" "$work/report_in.mlir" </dev/null \
        >"$work/stats.out" 2>"$work/stats.err" || true
    {
        echo "=== MLIR Optimization Report ==="
        echo "Input file: $out"
        echo "Pass pipeline: $pipeline"
        echo ""
        if [[ -s "$work/stats.out" ]]; then
            echo "Pass Statistics:"
            cat "$work/stats.out"
        fi
        if [[ -s "$work/stats.err" ]]; then
            echo "Diagnostics:"
            cat "$work/stats.err"
        fi
    } >&2
fi
exit 0
