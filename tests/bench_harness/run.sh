#!/usr/bin/env bash
# Tests for the cross-dimensional benchmark harness (scripts/tools/bench_harness,
# run as benchmarks/run_benchmarks.sh).
#
# Covers the pure functions through the tool's test modes (percentile,
# regression policy, system info) and a mock run against an empty repository
# root: output JSON shape, baseline comparison and exit codes. python and
# python3 are stubbed out on PATH: the harness must not need them.
#
# Usage: tests/bench_harness/run.sh
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/../.." && pwd -P)"
cd "$ROOT"

BIN="$ROOT/$(scripts/tools/build_tool.sh bench_harness)"

work="$(mktemp -d "${TMPDIR:-/tmp}/bench-harness-tests.XXXXXX")"
trap 'rm -rf "$work"' EXIT
stub="$work/bin"
mkdir -p "$stub"
for name in python python3; do
    printf '#!/bin/sh\necho "%s $*" >> "%s/python-calls.log"\nexit 127\n' "$name" "$work" > "$stub/$name"
    chmod +x "$stub/$name"
done
export PATH="$stub:$PATH"

pass=0
fail=0
check() {
    local name=$1 want=$2 got=$3
    if [[ "$want" == "$got" ]]; then
        pass=$((pass + 1))
    else
        fail=$((fail + 1))
        echo "FAIL $name: want [$want] got [$got]"
    fi
}

# --- get_percentile -------------------------------------------------------
check "percentile 0.5" "5.5" "$("$BIN" --percentile 0.5 1 2 3 4 5 6 7 8 9 10)"
p95="$("$BIN" --percentile 0.95 1 2 3 4 5 6 7 8 9 10)"
close="$(awk -v x="$p95" 'BEGIN { d = x - 9.55; if (d < 0) d = -d; print (d < 1e-9) ? "yes" : "no" }')"
check "percentile 0.95 close to 9.55 (got $p95)" "yes" "$close"
check "percentile of nothing" "0.0" "$("$BIN" --percentile 0.5)"
check "percentile unsorted input" "1.5" "$("$BIN" --percentile 0.25 3 1 2)"

# --- evaluate_regression --------------------------------------------------
workload() {
    printf '{"os": "%s", "cpu": "%s", "semantic_parity_status": "%s", "flow_metrics": {"median": %s}}\n' "$1" "$2" "$3" "$4"
}
workload Linux x86_64 verified 10.0 > "$work/old.json"
regress() {
    workload "$@" > "$work/new.json"
    "$BIN" --eval-regression "$work/old.json" "$work/new.json"
}
check "faster is pass" "pass" "$(regress Linux x86_64 verified 8.0)"
check "2% slower is within margin" "pass_within_margin" "$(regress Linux x86_64 verified 10.2)"
check "10% slower is a regression" "regression" "$(regress Linux x86_64 verified 11.0)"
check "other machine is skipped" "skipped_env_mismatch" "$(regress Darwin arm64 verified 11.0)"
check "failed runs are skipped" "skipped_unresolved_correctness" "$(regress Linux x86_64 unresolved 8.0)"
printf '{"os": "Linux", "cpu": "x86_64", "semantic_parity_status": "verified", "flow_metrics": {}}\n' > "$work/new.json"
check "no median is no_data" "no_data" "$("$BIN" --eval-regression "$work/old.json" "$work/new.json")"

# --- get_system_info ------------------------------------------------------
info="$("$BIN" --system-info)"
for key in os cpu arch flow_version git_sha python_version threads; do
    if grep -q "\"$key\": " <<< "$info"; then
        pass=$((pass + 1))
    else
        fail=$((fail + 1))
        echo "FAIL system info has no $key"
    fi
done

# --- a mock run: no cross_harness under the root --------------------------
empty="$work/root"
mkdir -p "$empty"
cd "$work"
set +e
out="$(FLOW_REPO_ROOT="$empty" "$BIN" --smoke --out mock.json)"
code=$?
set -e
check "mock run exit" "0" "$code"
check "mock run output" "Running benchmarks (smoke=True)...
python3 not found; skipping the Python subjects
No benchmarks found. Create some in benchmarks/cross_harness/
Wrote benchmark results to mock.json" "$out"
for key in '"timestamp": ' '"system": {' '"benchmarks": [' '"workload_id": "mock_workload"' \
    '"semantic_parity_status": "verified"' '"flow_command": "echo flow_mock"' \
    '"python_command": "echo python_mock"' '"warm_mode": true' '"repeats": 3' \
    '"flow_metrics": {' '"python_metrics": {' '"median": ' '"p95": ' '"dispersion": ' \
    '"allocations": 0' '"copies": 0'; do
    if grep -qF "$key" mock.json; then
        pass=$((pass + 1))
    else
        fail=$((fail + 1))
        echo "FAIL mock.json has no $key"
    fi
done

# A baseline far faster than anything real: a regression and exit 1.
sed -E 's/("median": )[0-9.e+-]+/\11e-09/' mock.json > fast.json
set +e
out="$(FLOW_REPO_ROOT="$empty" "$BIN" --smoke --baseline fast.json --out new.json)"
code=$?
set -e
check "regression exit" "1" "$code"
check "regression line" "mock_workload: regression" "$(grep '^mock_workload:' <<< "$out")"
check "regression detail" "yes" "$(grep -q '^  Regression found! Old median: 1e-09, New median: ' <<< "$out" && echo yes || echo no)"

# A baseline far slower: pass.
sed -E 's/("median": )[0-9.e+-]+/\1100.0/' mock.json > slow.json
set +e
out="$(FLOW_REPO_ROOT="$empty" "$BIN" --smoke --baseline slow.json --out new.json)"
code=$?
set -e
check "pass exit" "0" "$code"
check "pass line" "mock_workload: pass" "$(grep '^mock_workload:' <<< "$out")"

set +e
out="$(FLOW_REPO_ROOT="$empty" "$BIN" --smoke --baseline missing.json --out new.json)"
code=$?
set -e
check "missing baseline exit" "0" "$code"
check "missing baseline line" "Baseline file missing.json not found." "$(grep '^Baseline' <<< "$out")"

set +e
FLOW_REPO_ROOT="$empty" "$BIN" --bogus > /dev/null 2>&1
code=$?
set -e
check "unknown argument exit" "2" "$code"

cd "$ROOT"
if [[ -f "$work/python-calls.log" ]] && grep -qv -- "--version$" "$work/python-calls.log"; then
    fail=$((fail + 1))
    echo "FAIL python was invoked other than the availability probe:"
    grep -v -- "--version$" "$work/python-calls.log"
fi

echo "bench_harness: pass=$pass fail=$fail"
[[ "$fail" -eq 0 ]]
