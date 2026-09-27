#!/usr/bin/env bash
# Prove that the default `./flow run` and `./flow compile` paths need no Python.
#
# Puts stub `python` and `python3` first on PATH. Each stub logs its arguments
# and exits 127. Then, from a clean compiler/build and build/, it builds flowc
# from the checked-in bootstrap C (through ensure_flowc, as a user's first
# `flow run` would) and runs a set of programs:
#
#   - a program with no imports, from the repository root and from another
#     working directory;
#   - a program whose exit status is its result (fibonacci, 55), through both
#     `flow run` and `flow compile`;
#   - programs that import stdlib modules;
#   - a project with its own flow.toml and an empty [dependencies] table;
#   - a project that declares a registry package, already installed and
#     locked, so `flow run` has to decide on its own that nothing needs
#     syncing.
#
# A final control removes that project's installed package and checks that
# `flow run` still hands it to the package manager (the stub logs the call).
#
# Passes only when every program behaves as expected and no stub was called.
#
#   ./scripts/check_run_without_python.sh            # clean build first
#   ./scripts/check_run_without_python.sh --keep     # reuse compiler/build

set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT" || exit 1

keep=0
[[ "${1:-}" == "--keep" ]] && keep=1

work="$(mktemp -d "${TMPDIR:-/tmp}/flow-nopy.XXXXXX")"
trap 'rm -rf "$work"' EXIT

stub_dir="$work/bin"
log="$work/python-calls.log"
mkdir -p "$stub_dir"
: > "$log"
for name in python python3; do
    cat > "$stub_dir/$name" <<EOF
#!/bin/sh
echo "$name \$*" >> "$log"
exit 127
EOF
    chmod +x "$stub_dir/$name"
done
export PATH="$stub_dir:$PATH"
unset FLOW_HOST FLOWC_BIN FLOW_RUN_PYTHON

if [[ "$(command -v python3)" != "$stub_dir/python3" ]]; then
    echo "check_run_without_python: stub python3 is not first on PATH" >&2
    exit 1
fi

if [[ "$keep" -eq 0 ]]; then
    rm -rf compiler/build build
fi

fail=0
pass=0

# expect_exit <want> <label> <command...>
expect_exit() {
    local want="$1" label="$2"
    shift 2
    local out="$work/out.txt" rc=0
    "$@" > "$out" 2>&1 || rc=$?
    if [[ "$rc" -eq "$want" ]]; then
        echo "PASS $label (exit $rc)"
        pass=$((pass + 1))
    else
        echo "FAIL $label (exit $rc, want $want)"
        tail -n 20 "$out" | sed 's/^/     /'
        fail=$((fail + 1))
    fi
}

# Program with no imports.
expect_exit 0 "run examples/basics/hello_world.flow" \
    ./flow run examples/basics/hello_world.flow
cd "$work" || exit 1
expect_exit 0 "run hello_world.flow from another directory" \
    "$ROOT/flow" run "$ROOT/examples/basics/hello_world.flow"
cd "$ROOT" || exit 1

# Exit status carries the result.
expect_exit 55 "run examples/basics/fibonacci.flow" \
    ./flow run examples/basics/fibonacci.flow
expect_exit 0 "compile examples/basics/fibonacci.flow" \
    ./flow compile examples/basics/fibonacci.flow
expect_exit 55 "execute build/fibonacci" ./build/fibonacci

# Programs that import stdlib modules.
expect_exit 0 "run examples/basics/result_pipeline.flow (import stdlib/result)" \
    ./flow run examples/basics/result_pipeline.flow
expect_exit 0 "run examples/dsp/pipeline.flow (import stdlib/dsp)" \
    ./flow run examples/dsp/pipeline.flow

# A standalone project with its own manifest and no dependencies.
proj="$work/empty_deps"
mkdir -p "$proj/src"
cat > "$proj/flow.toml" <<'EOF'
[package]
name = "empty_deps"
version = "0.1.0"
entry = "src/main.flow"

[dependencies]

[dev-dependencies]
EOF
cat > "$proj/src/main.flow" <<'EOF'
function main() -> i32 {
    return 7
}
EOF
expect_exit 7 "run project with empty [dependencies]" \
    ./flow run "$proj/src/main.flow"

# A project that declares a registry package which is already installed and
# locked. Installing it is what `flow sync` does; this checks that `flow run`
# recognises there is nothing left to do. The program does not import the
# package: flowc cannot yet resolve package imports such as `json.lib`.
proj="$work/registry_dep"
mkdir -p "$proj/src" "$proj/flow_packages"
cat > "$proj/flow.toml" <<'EOF'
[package]
name = "registry_dep"
version = "0.1.0"
entry = "src/main.flow"

[dependencies]
json = "0.1.0"

[dev-dependencies]
EOF
cat > "$proj/flow.lock" <<EOF
{
  "version": 1,
  "packages": {
    "json": {
      "version": "0.1.0",
      "source": "registry",
      "resolved": {
        "path": "$ROOT/registry/packages/json"
      }
    }
  }
}
EOF
cp -R registry/packages/json "$proj/flow_packages/json"
cat > "$proj/src/main.flow" <<'EOF'
function main() -> i32 {
    return 3
}
EOF
expect_exit 3 "run project with installed registry dependency (json)" \
    ./flow run "$proj/src/main.flow"

# Control: a project whose dependency is not installed still goes to the full
# package manager, as before (exit 127 is the stub's). That call must show up in the
# log, which also shows the stubs catch what they are meant to catch.
cp "$log" "$work/before-control.log"
rm -rf "$proj/flow_packages"
expect_exit 127 "control: missing dependency is handed to the package manager" \
    ./flow run "$proj/src/main.flow"
if grep -q "^python3 -m flow.package sync --program" "$log"; then
    echo "PASS control: stub logged the package manager call"
    pass=$((pass + 1))
else
    echo "FAIL control: expected a logged python3 -m flow.package sync call"
    fail=$((fail + 1))
fi
cp "$work/before-control.log" "$log"

echo
echo "programs: pass=$pass fail=$fail"
if [[ -s "$log" ]]; then
    echo "python stubs were called:"
    sed 's/^/  /' "$log"
    exit 1
fi
echo "python stubs called: 0"
if [[ "$fail" -ne 0 ]]; then
    exit 1
fi
echo "check_run_without_python: PASS"
