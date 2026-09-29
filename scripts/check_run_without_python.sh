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
#   - a project that declares a registry package, imports it
#     (`import json.lib`) and has nothing installed yet, so `flow run` must
#     install it, write flow.lock and resolve the import; then the same
#     project again, already installed;
#   - `flow sync`, `flow add`, `flow pkg install`, `flow search`, `flow info`;
#   - a project with an unknown dependency, which must fail with the package
#     manager's message.
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

# The language suite on the flowc host (opt-in; Python strict is its default).
expect_exit 0 "FLOW_HOST=flowc test-lang tests/lang/test_strings.flow" \
    env FLOW_HOST=flowc ./flow test-lang tests/lang/test_strings.flow

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

# A project that declares a registry package and imports it. Nothing is
# installed yet: `flow run` has to install the package (the Flow package
# manager, compiler/src/pkg.flow), write flow.lock, resolve `import json.lib`
# from flow_packages/ in flowc, and run the program.
proj="$work/registry_dep"
mkdir -p "$proj/src"
cat > "$proj/flow.toml" <<'EOF'
[package]
name = "registry_dep"
version = "0.1.0"
entry = "src/main.flow"

[dependencies]
json = "0.1.0"

[dev-dependencies]
EOF
cat > "$proj/src/main.flow" <<'EOF'
import json.lib { json_get_i32, json_validate }

function main() -> i32 {
    let doc: string = "{\"answer\": 3}"
    if json_validate(doc) != 1 {
        return 1
    }
    return json_get_i32(doc, "answer")
}
EOF
expect_exit 3 "run project importing a registry package that is not installed (json)" \
    ./flow run "$proj/src/main.flow"

expected_lock="$work/expected.lock"
cat > "$expected_lock" <<EOF
{
  "version": 1,
  "packages": {
    "json": {
      "version": "0.1.0",
      "source": "registry",
      "resolved": {
        "path": "$(cd "$ROOT" && pwd -P)/registry/packages/json"
      }
    }
  }
}
EOF
if cmp -s "$expected_lock" "$proj/flow.lock" && \
        diff -r "$ROOT/registry/packages/json" "$proj/flow_packages/json" >/dev/null; then
    echo "PASS flow.lock and flow_packages/json written"
    pass=$((pass + 1))
else
    echo "FAIL flow.lock or flow_packages/json not as expected"
    diff "$expected_lock" "$proj/flow.lock" | sed 's/^/     /' || true
    fail=$((fail + 1))
fi

# Second run: everything is installed and locked, so nothing is fetched.
expect_exit 3 "run the same project again (already installed)" \
    ./flow run "$proj/src/main.flow"

# The package commands themselves.
proj2="$work/pkg_cmds"
mkdir -p "$proj2/src"
cp "$proj/flow.toml" "$proj2/flow.toml"
cd "$proj2" || exit 1
expect_exit 0 "flow sync" "$ROOT/flow" sync
expect_exit 0 "flow add toml" "$ROOT/flow" add toml
expect_exit 0 "flow pkg install" "$ROOT/flow" pkg install
expect_exit 0 "flow search json" "$ROOT/flow" search json
expect_exit 0 "flow info json" "$ROOT/flow" info json
cd "$ROOT" || exit 1
if [[ -d "$proj2/flow_packages/toml" ]] && grep -q '"toml"' "$proj2/flow.lock"; then
    echo "PASS flow add installed and locked toml"
    pass=$((pass + 1))
else
    echo "FAIL flow add did not install and lock toml"
    fail=$((fail + 1))
fi

# A dependency that does not exist fails with the package manager's message.
proj3="$work/unknown_dep"
mkdir -p "$proj3/src"
sed 's/^json = "0.1.0"$/no_such_package = "1.0.0"/' "$proj/flow.toml" > "$proj3/flow.toml"
printf 'function main() -> i32 {\n    return 0\n}\n' > "$proj3/src/main.flow"
expect_exit 1 "run project with an unknown dependency fails" \
    ./flow run "$proj3/src/main.flow"
if grep -q "Unknown dependency 'no_such_package'" "$work/out.txt"; then
    echo "PASS unknown dependency is reported"
    pass=$((pass + 1))
else
    echo "FAIL unknown dependency message missing"
    fail=$((fail + 1))
fi

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
