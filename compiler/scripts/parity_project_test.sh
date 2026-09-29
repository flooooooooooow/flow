#!/usr/bin/env bash
# Parity gate for the project test runner (`flow test` outside the Flow
# repository), tools/project_test/main.flow.
#
# The runner was src/flow/project_test_runner.py. This gate builds a set of
# small projects under compiler/build/parity_project_test and runs `flow test`
# in each with a list of argument sets, covering discovery, native `test`
# blocks, program tests, goldens (.expected, .expected-stderr, .exitcode),
# compile failures, timeouts, filters, [test] configuration, --list,
# --verbose, --fail-fast, --keep and argument errors. Each result is the
# normalised stdout, stderr and exit code, compared with the goldens in
# tests/project_test/golden/.
#
#   ./compiler/scripts/parity_project_test.sh
#       run the Flow runner with python and python3 stubbed out on PATH.
#
#   ./compiler/scripts/parity_project_test.sh --write-golden <rev>
#       rewrite the goldens from the Python runner at git revision <rev>
#       (the last one is e6a7f046).
#
# Normalised: durations (N.NNNs), the random part of native-test wrapper
# names, and the absolute path of the work directory.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
cd "$ROOT"

GOLD="$ROOT/tests/project_test/golden"
WORK="$ROOT/compiler/build/parity_project_test"
mode="${1:-}"
rev="${2:-}"

rm -rf "$WORK"
mkdir -p "$WORK"

# ---------------------------------------------------------------- projects
mk() { mkdir -p "$(dirname "$1")"; cat > "$1"; }

# p_main: every kind of case in one tests/ directory.
P="$WORK/p_main"
mk "$P/flow.toml" <<'EOF'
[package]
name = "p_main"
version = "0.1.0"
EOF
mk "$P/tests/native.flow" <<'EOF'
function helper() -> i32 { return 42 }

test "answer is right" {
    expect helper() == 42
}

test "answer is wrong" {
    expect helper() == 41
}

  test "Delay: \"quoted\" name!" {
    expect helper() > 0
}

test "answer is right" {
    expect helper() != 0
}
EOF
mk "$P/tests/prog.flow" <<'EOF'
function main() -> i32 {
    println("hello")
    return 0
}
EOF
printf 'hello\n' > "$P/tests/prog.expected"
# The second "answer is right" has the slug answer_is_right_2.
printf 'not printed\n' > "$P/tests/native.answer_is_right_2.expected"
mk "$P/tests/mismatch.flow" <<'EOF'
function main() -> i32 {
    println("actual line")
    return 0
}
EOF
printf 'expected line\n' > "$P/tests/mismatch.expected"
mk "$P/tests/exits.flow" <<'EOF'
function main() -> i32 {
    println("three")
    return 3
}
EOF
printf '3\n' > "$P/tests/exits.exitcode"
mk "$P/tests/wrong_exit.flow" <<'EOF'
function main() -> i32 {
    println("line one")
    println("line two")
    return 7
}
EOF
mk "$P/tests/bad.flow" <<'EOF'
function main() -> i32 {
    let x: i32 = undefined_name
    return x
}
EOF
mk "$P/tests/native_golden.flow" <<'EOF'
test "prints things" {
    println("from test")
    expect 1 == 1
}
EOF
printf 'from test\n' > "$P/tests/native_golden.prints_things.expected"
mk "$P/tests/badexit.flow" <<'EOF'
function main() -> i32 {
    return 0
}
EOF
printf 'abc\n' > "$P/tests/badexit.exitcode"
mk "$P/tests/_helper.flow" <<'EOF'
function main() -> i32 { return 1 }
EOF
mk "$P/tests/wip/later.flow" <<'EOF'
function main() -> i32 { return 1 }
EOF
mk "$P/tests/build/skip.flow" <<'EOF'
function main() -> i32 { return 1 }
EOF
mk "$P/tests/sub/deeper.flow" <<'EOF'
function main() -> i32 {
    println("deep")
    return 0
}
EOF
mk "$P/tests/library.flow" <<'EOF'
function not_a_test() -> i32 { return 1 }
EOF
mk "$P/other/extra.flow" <<'EOF'
function main() -> i32 { return 0 }
EOF

# p_config: [test] paths as a string, a timeout, a program that loops.
P="$WORK/p_config"
mk "$P/flow.toml" <<'EOF'
[package]
name = "p_config"

[test]
paths = "checks"
timeout = 4
EOF
mk "$P/checks/fast.flow" <<'EOF'
function main() -> i32 {
    return 0
}
EOF
mk "$P/checks/slow.flow" <<'EOF'
extern {
    function usleep(us: i32) -> i32
}

function main() -> i32 {
    println("before the loop")
    let mut i: i64 = 0
    while i >= 0 {
        usleep(1000)
        i = i + 1
        if i > 1000000 {
            i = 1
        }
    }
    return 0
}
EOF

# p_paths: [test] paths as an array, one missing directory.
P="$WORK/p_paths"
mk "$P/flow.toml" <<'EOF'
[package]
name = "p_paths"

[test]
paths = ["unit", "missing", "integration"]
backend = "c"
EOF
mk "$P/unit/u.flow" <<'EOF'
test "unit ok" {
    expect 2 + 2 == 4
}
EOF
mk "$P/integration/i.flow" <<'EOF'
extern {
    function write(fd: i32, buf: string, n: i64) -> i64
}

function main() -> i32 {
    write(2, "to stderr\n", 10)
    return 0
}
EOF
printf 'to stderr\n' > "$P/integration/i.expected-stderr"

# p_empty: no tests at all.
P="$WORK/p_empty"
mk "$P/flow.toml" <<'EOF'
[package]
name = "p_empty"
EOF
mkdir -p "$P/src"

# Bad [test] values.
mk "$WORK/p_cfg_backend/flow.toml" <<'EOF'
[package]
name = "p_cfg_backend"

[test]
backend = "x"  # not a backend
EOF
mk "$WORK/p_cfg_timeout/flow.toml" <<'EOF'
[test]
timeout = "abc"
EOF
mk "$WORK/p_cfg_paths/flow.toml" <<'EOF'
[package]
name = "p_cfg_paths"
[test]
paths = 5
[other]
paths = "x"
EOF

# p_main_rename: a native test file that also defines main().
P="$WORK/p_rename"
mk "$P/flow.toml" <<'EOF'
[package]
name = "p_rename"
EOF
mk "$P/tests/both.flow" <<'EOF'
function main() -> i32 {
    return 9
}

test "still runs" {
    expect 1 == 1
}
EOF

# ---------------------------------------------------------------- cases
# name|project|args (split on spaces; no quoting needed)
CASES='
list|p_main|--list
list_all|p_main|--list --backend all
run|p_main|
verbose|p_main|-v tests/prog.flow tests/native_golden.flow
failfast|p_main|--fail-fast tests/wrong_exit.flow tests/prog.flow
filter_sub|p_main|--filter ANSWER
filter_short|p_main|-f prog
filter_eq|p_main|--filter=deeper
filter_glob|p_main|-f tests/n*::*right
filter_none|p_main|-f nothing_matches
explicit_dir|p_main|other
explicit_missing|p_main|nowhere
keep|p_main|--keep -f quoted
config_timeout|p_config|
config_cli_timeout|p_config|--timeout 2.5 -f slow
paths_array|p_paths|
paths_list|p_paths|--list
empty|p_empty|
empty_list|p_empty|--list
rename|p_rename|
cfg_backend|p_cfg_backend|
cfg_timeout|p_cfg_timeout|
cfg_paths|p_cfg_paths|
abbrev|p_main|--fil prog --verb
ambiguous|p_main|--f prog
dashdash|p_main|-- tests/prog.flow
help|p_main|-h
bogus|p_main|--bogus
bad_backend|p_main|--backend x
bad_profile|p_main|--profile none
bad_timeout|p_main|--timeout abc
missing_value|p_main|--filter
'

stub_dir="$WORK/stubbin"
mkdir -p "$stub_dir"
for name in python python3; do
    cat > "$stub_dir/$name" <<EOF
#!/bin/sh
echo "$name \$*" >> "$WORK/python-calls.log"
exit 127
EOF
    chmod +x "$stub_dir/$name"
done

pysrc=""
if [[ "$mode" == "--write-golden" ]]; then
    [[ -n "$rev" ]] || { echo "usage: $0 --write-golden <rev>" >&2; exit 2; }
    pysrc="$WORK/pysrc"
    mkdir -p "$pysrc"
    git archive "$rev" src/flow | tar -x -C "$pysrc"
    mkdir -p "$GOLD"
fi

normalise() {
    sed -E \
        -e "s#$WORK#<WORK>#g" \
        -e "s#$ROOT#<ROOT>#g" \
        -e 's/[0-9]+\.[0-9]{3}s/N.NNNs/g' \
        -e 's/(\.flow_test_[A-Za-z0-9_]+_[0-9]+_)[A-Za-z0-9_]+\.flow/\1RAND.flow/g'
}

run_case() {
    local name="$1" proj="$2" args="$3"
    local out="$WORK/out/$name"
    mkdir -p "$out"
    local rc=0
    set -f
    # shellcheck disable=SC2086
    if [[ -n "$pysrc" ]]; then
        (cd "$WORK/$proj" && FLOW_TEST_DRIVER="$ROOT/flow-driver" \
            FLOW_TEST_BUILD_DIR="$ROOT/build" PYTHONPATH="$pysrc/src" \
            python3 -m flow.project_test_runner $args \
            >"$out/stdout" 2>"$out/stderr") || rc=$?
    else
        (cd "$WORK/$proj" && PATH="$stub_dir:$PATH" "$ROOT/flow" test $args \
            >"$out/stdout" 2>"$out/stderr") || rc=$?
    fi
    {
        echo "exit=$rc"
        echo "--- stdout"
        normalise < "$out/stdout"
        echo "--- stderr"
        normalise < "$out/stderr"
        if [[ "$name" == keep ]]; then
            echo "--- kept wrappers"
            (cd "$WORK/$proj" && find tests -name '.flow_test_*' | normalise | sort)
            echo "--- wrapper text"
            find "$WORK/$proj" -name '.flow_test_*' -exec cat {} \;
            find "$WORK/$proj" -name '.flow_test_*' -delete
        fi
    } > "$out/result"
    set +f
}

# Build flowc (and the runner tool) outside the cases, so no case sees the
# one-time build messages.
"$ROOT/flow-driver" compile "$WORK/p_main/tests/prog.flow" >/dev/null 2>&1 || true
if [[ -z "$pysrc" ]]; then
    (cd "$WORK/p_empty" && PATH="$stub_dir:$PATH" "$ROOT/flow" test --list >/dev/null 2>&1) || true
fi

fail=0
pass=0
while IFS='|' read -r name proj args; do
    [[ -n "$name" ]] || continue
    run_case "$name" "$proj" "$args"
    if [[ -n "$pysrc" ]]; then
        cp "$WORK/out/$name/result" "$GOLD/$name.txt"
        echo "wrote $name"
    elif cmp -s "$WORK/out/$name/result" "$GOLD/$name.txt"; then
        pass=$((pass + 1))
    else
        fail=$((fail + 1))
        echo "FAIL $name"
        diff -u "$GOLD/$name.txt" "$WORK/out/$name/result" | head -40 || true
    fi
done <<< "$CASES"

if [[ -n "$pysrc" ]]; then
    exit 0
fi
if [[ -s "$WORK/python-calls.log" ]]; then
    echo "FAIL python was called:" >&2
    cat "$WORK/python-calls.log" >&2
    exit 1
fi
echo "parity_project_test: $pass passed, $fail failed"
[[ "$fail" -eq 0 ]]
