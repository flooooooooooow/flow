#!/usr/bin/env bash
# Parity gate for the package commands that moved from src/flow/package.py
# and src/flow/registry.py to the Flow package manager (compiler/src/pkg.flow):
# init, publish, build, build-native, run-native, clean, and `flow pkg` for
# the same commands plus `run`.
#
# Each case builds a small project, runs one command in it and records
# stdout, the exit status and the files the command wrote (flow.toml, the
# scaffold, a registry index, the build/ listing). Goldens live in
# tests/pkg_commands/<case>.expect with the repository path written as @ROOT@
# and the scratch directory outside the repository as @OUT@.
#
#   scripts/check_pkg_commands.sh            run the Flow commands with
#                                            python and python3 stubbed out
#                                            and compare against the goldens
#   scripts/check_pkg_commands.sh --record   write the goldens from the
#                                            Python package manager at
#                                            PARITY_REF (needs python3 and git)
#
# Deliberate differences from the Python reference, applied when recording:
#   - `flow init` writes host = "flowc" in [build]. The Python version wrote
#     host = "python", a host #1027 retired; `flow add` already rewrites the
#     manifest with "flowc".
set -uo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd -P)"
cd "$ROOT" || exit 1

# The last commit whose src/flow/package.py held these commands.
PARITY_REF="${PARITY_REF:-e6a7f046}"
GOLD="$ROOT/tests/pkg_commands"

mode=check
[[ "${1:-}" == "--record" ]] && mode=record

work="$ROOT/build/pkg-commands"
rm -rf "$work"
mkdir -p "$work"
out_dir="$(mktemp -d "${TMPDIR:-/tmp}/flow-pkg-cmds.XXXXXX")"
out_dir="$(cd "$out_dir" && pwd -P)"
ref="$ROOT/build/pkgref"
trap 'rm -rf "$out_dir" "$ref"' EXIT

unset FLOW_REGISTRY_URL FLOW_REGISTRY_PATH FLOW_HOST FLOW_RUN_PYTHON

if [[ "$mode" == record ]]; then
    # The Python package manager, placed so that its repository root
    # (three parents up from package.py) is this checkout.
    rm -rf "$ref"
    mkdir -p "$ref"
    : > "$ref/__init__.py"
    for f in package.py registry.py toml_compat.py; do
        git show "$PARITY_REF:src/flow/$f" > "$ref/$f" || {
            echo "check_pkg_commands: cannot read $f at $PARITY_REF"; exit 1; }
    done
    mkdir -p "$GOLD"
else
    stub_dir="$out_dir/stub-bin"
    stub_log="$out_dir/python-calls.log"
    mkdir -p "$stub_dir"
    : > "$stub_log"
    for name in python python3; do
        printf '#!/bin/sh\necho "%s $*" >> "%s"\nexit 127\n' "$name" "$stub_log" > "$stub_dir/$name"
        chmod +x "$stub_dir/$name"
    done
    export PATH="$stub_dir:$PATH"
    # Build the package manager once, outside the timed cases.
    (cd "$out_dir" && bash "$ROOT/flow-driver" info hello_lib >/dev/null 2>&1)
fi

# flow <command> [args...], run in the current directory by the side under
# test. On the Python side each command is invoked as flow-driver invoked it.
flowcmd() {
    if [[ "$mode" == check ]]; then
        if [[ "$1" == demo-run-native ]]; then
            # flow-driver's demo launchers: cd DIR, then run-native ENTRY.
            cd "$2" && bash "$ROOT/flow" run-native "$3"
            return $?
        fi
        bash "$ROOT/flow" "$@"
        return $?
    fi
    local cmd="$1"
    shift
    local py=(env PYTHONUNBUFFERED=1 PYTHONPATH="$ROOT/build" python3)
    case "$cmd" in
        init|publish) "${py[@]}" -m pkgref.package "$cmd" "$@" ;;
        build) "${py[@]}" -m pkgref.package build ;;
        pkg) "${py[@]}" -m pkgref.package "$@" ;;
        build-native|run-native)
            local meth="${cmd/-/_}"
            "${py[@]}" -c "
import sys
arg = sys.argv[1] if len(sys.argv) > 1 and sys.argv[1] != '' else None
from pkgref.package import FlowPackageManager
FlowPackageManager().$meth(arg)
" "${1-}" ;;
        clean) "${py[@]}" -c "
from pkgref.package import FlowPackageManager
FlowPackageManager().clean()
" ;;
        demo-run-native)
            # flow-driver's demo launchers: FlowPackageManager(DIR).run_native(ENTRY)
            "${py[@]}" -c "
import sys
from pkgref.package import FlowPackageManager
FlowPackageManager(sys.argv[1]).run_native(sys.argv[2])
" "$1" "$2" ;;
        *) echo "unknown command $cmd" ; return 99 ;;
    esac
}

normalize() {
    sed -E -e "s#$out_dir#@OUT@#g" -e "s#$ROOT#@ROOT@#g" -e "s#/run\.[A-Za-z0-9]{6}/#/run.XXXXXX/#g" \
        -e "s#flowc emit via [^ ]*flowc[^ ]*#flowc emit via FLOWC#" \
        -e "/^ensure_flowc: compiler\/src has local edits/d"
}

# Files a command may have written, relative to the project directory.
snapshot() {
    local dir="$1"
    (
        cd "$dir" || exit 1
        find . -path ./flow_packages -prune -o -print | LC_ALL=C sort | while IFS= read -r p; do
            [[ "$p" == "." ]] && continue
            if [[ -d "$p" ]]; then
                echo "D $p"
            elif [[ "$p" == ./build/* ]]; then
                echo "F $p"
            else
                echo "F $p"
                sed 's/^/  | /' "$p"
            fi
        done
    )
}

pass=0
fail=0
current=""
result=""

# Start a case: a fresh project directory ($dir) under the repository (or
# outside it with `begin NAME outside`).
begin() {
    current="$1"
    if [[ "${2:-}" == outside ]]; then
        dir="$out_dir/$1"
    else
        dir="$work/$1"
    fi
    rm -rf "$dir"
    mkdir -p "$dir"
    result="$work/$1.result"
    : > "$result"
}

# run [ENV=VAL...] -- flow-args...: run one command in $dir and log it.
run() {
    local envs=()
    while [[ $# -gt 0 && "$1" != "--" ]]; do
        envs+=("$1")
        shift
    done
    shift
    local rc=0 so="$work/$current.stdout"
    {
        echo "\$ flow $*" | normalize
    } >> "$result"
    (
        cd "$dir" || exit 1
        for e in ${envs[@]+"${envs[@]}"}; do
            export "${e?}"
        done
        flowcmd "$@"
    ) > "$so" 2>/dev/null || rc=$?
    normalize < "$so" >> "$result"
    echo "[exit $rc]" >> "$result"
}

# Record the files and compare (or store) the golden.
finish() {
    local extra="${1:-}"
    {
        echo "== files"
        snapshot "$dir" | normalize
        if [[ -n "$extra" && -f "$extra" ]]; then
            echo "== $(basename "$extra")"
            normalize < "$extra"
        fi
    } >> "$result"
    if [[ "$mode" == record ]]; then
        sed -e 's/^  | host = "python"$/  | host = "flowc"/' "$result" > "$GOLD/$current.expect"
        echo "recorded $current"
        return
    fi
    if cmp -s "$result" "$GOLD/$current.expect"; then
        echo "PASS $current"
        pass=$((pass + 1))
    else
        echo "FAIL $current"
        diff "$GOLD/$current.expect" "$result" | head -40 | sed 's/^/     /'
        fail=$((fail + 1))
    fi
}

hello_main() {
    mkdir -p "$dir/src"
    cat > "$dir/src/main.flow" <<'EOF'
function main() -> i32 {
    printf("hello from the project\n")
    return 0
}
EOF
}

manifest() {
    # manifest NAME [extra toml...]
    local name="$1"
    shift
    {
        echo "[package]"
        echo "name = \"$name\""
        echo "version = \"0.3.1\""
        echo "description = \"Test package $name\""
        echo "license = \"Apache-2.0\""
        echo "entry = \"src/main.flow\""
        echo ""
        printf '%s\n' "$@"
    } > "$dir/flow.toml"
}

# ---------------------------------------------------------------- init
begin init_default
run -- init
finish

begin init_named
run -- init coolname
finish

begin init_existing
manifest already
run -- init
finish

begin init_keeps_files
mkdir -p "$dir/src"
echo "# mine" > "$dir/src/main.flow"
echo "mine/" > "$dir/.gitignore"
run -- init keep
finish

begin init_extra_args
run -- init one two
finish

begin pkg_init
run -- pkg init viapkg
finish

# ---------------------------------------------------------------- publish
begin publish_no_toml
run -- publish --dry-run
finish

begin publish_outside_repo outside
manifest outsider
run -- publish
finish

begin publish_inside_dry_run
manifest insider
run -- publish --dry-run
finish

begin publish_git_dry_run outside
manifest gitdry
run -- publish --git https://example.com/gitdry.git --tag v0.3.1 --dry-run
finish

begin publish_git_new_index outside
manifest gitpkg
run FLOW_REGISTRY_PATH="$out_dir/publish_git_new_index/reg/index.json" -- \
    publish --git https://example.com/gitpkg.git --tag v0.3.1
finish

begin publish_inside_repo
manifest insidepkg
idx="$work/publish_inside_repo.index.json"
cat > "$idx" <<'EOF'
{
  "version": 1,
  "name": "test-index",
  "packages": {
    "other": {
      "description": "Other",
      "homepage": "https://example.com",
      "license": "MIT",
      "versions": [
        {"version": "1.0.0", "yanked": false, "path": "x"}
      ]
    },
    "insidepkg": {
      "description": "Old description",
      "homepage": "https://example.com/insidepkg",
      "license": "MIT",
      "versions": [
        {"version": "0.1.0", "yanked": false, "path": "old"},
        {"version": "0.3.1", "yanked": true, "path": "stale"},
        {"version": "1.0.0-beta", "yanked": false, "git": "g", "tag": "t"},
        {"version": "0.10.0", "yanked": false, "path": "ten"},
        {"version": "v0.3.1+meta", "yanked": false, "path": "meta"}
      ]
    }
  }
}
EOF
run FLOW_REGISTRY_PATH="$idx" -- publish
finish "$idx"

begin publish_path_legacy_index outside
manifest legacy
idx="$out_dir/legacy_index.json"
cat > "$idx" <<'EOF'
{"version": 1, "crates": {"legacy": {"description": "", "license": "", "versions": [{"version": "0.3.1"}]}}}
EOF
run FLOW_REGISTRY_PATH="$idx" -- publish --path packages/legacy
finish "$idx"

begin publish_git_path_both outside
manifest both
idx="$out_dir/both_index.json"
run FLOW_REGISTRY_PATH="$idx" -- publish --path p/both --git https://example.com/both.git
finish "$idx"

begin publish_pkg_git_no_tag outside
manifest notag
idx="$out_dir/notag_index.json"
run FLOW_REGISTRY_PATH="$idx" -- pkg publish --git https://example.com/notag.git
finish "$idx"

# ---------------------------------------------------------------- build
begin build_no_toml
run -- build
finish

begin build_missing_entry
manifest nobuild
run -- build
finish

begin build_ok
manifest builds
hello_main
run -- build
finish

begin build_fail
manifest broken
mkdir -p "$dir/src"
echo 'function main() -> i32 { return }}' > "$dir/src/main.flow"
run -- build
finish

begin pkg_build_release
manifest relbuild
hello_main
run -- pkg build --release
finish

begin pkg_run
manifest runs
hello_main
run -- pkg run
finish

begin pkg_unknown
run -- pkg frobnicate
finish

# ---------------------------------------------------------------- native
native_project() {
    # A project with a C source, a dependency with native sources and flags,
    # and one missing source on each side.
    manifest "$1" \
        '[dependencies]' \
        'dep1 = { path = "../dep1" }' \
        'nodep = "1.0"' \
        '' \
        '[native]' \
        'sources = ["native/add.c", "native/missing.c"]' \
        'libs = ["m", "m"]' \
        'cflags = ["-DPROJECT_FLAG=1"]' \
        'ldflags = ["-L."]'
    mkdir -p "$dir/src" "$dir/native" "$dir/flow_packages/dep1"
    cat > "$dir/src/main.flow" <<'EOF'
extern {
    function native_add(a: i32, b: i32) -> i32
    function dep_mul(a: i32, b: i32) -> i32
}

function main() -> i32 {
    printf("sum %d product %d\n", native_add(2, 3), dep_mul(4, 5))
    return 3
}
EOF
    cat > "$dir/native/add.c" <<'EOF'
#ifndef PROJECT_FLAG
#error project cflags missing
#endif
int native_add(int a, int b) { return a + b; }
EOF
    cat > "$dir/flow_packages/dep1/flow.toml" <<'EOF'
[package]
name = "dep1"

[native]
sources = ["dep.c", "gone.c", "dep.c"]
libs = ["m"]
cflags = ["-DDEP_FLAG=2"]
EOF
    cat > "$dir/flow_packages/dep1/dep.c" <<'EOF'
#if DEP_FLAG != 2
#error dep cflags missing
#endif
int dep_mul(int a, int b) { return a * b; }
EOF
}

begin build_native_c
native_project nativec
run -- build-native
finish

begin run_native_c
native_project runc
run -- run-native
finish

begin build_native_entry_arg
native_project entryarg
cp "$dir/src/main.flow" "$dir/other.flow"
run -- build-native other.flow
finish

begin build_native_missing_entry
native_project missingentry
run -- build-native nosuch.flow
finish

begin build_native_no_toml
run -- build-native
finish

begin build_native_flowc_fail
manifest flowcfail
mkdir -p "$dir/src"
echo 'function main() -> i32 { return }}' > "$dir/src/main.flow"
run -- build-native
finish

begin build_native_cc_fail
manifest ccfail '[native]' 'sources = ["bad.c"]'
hello_main
echo 'int broken( {' > "$dir/bad.c"
run -- build-native
finish

begin build_native_cxx
manifest cxx '[native]' 'sources = ["native/add.cpp"]' 'cflags = ["-std=c++17", "-DCXX_FLAG=1"]'
mkdir -p "$dir/src" "$dir/native"
cat > "$dir/src/main.flow" <<'EOF'
extern {
    function native_add(a: i32, b: i32) -> i32
}

function main() -> i32 {
    printf("cxx sum %d\n", native_add(20, 22))
    return 0
}
EOF
cat > "$dir/native/add.cpp" <<'EOF'
#include <vector>
extern "C" int native_add(int a, int b) { std::vector<int> v{a, b}; return v[0] + v[1]; }
EOF
run -- run-native
finish

begin pkg_build_native_release
manifest pkgrel
hello_main
run -- pkg build-native --release
finish

begin demo_run_native
native_project demo
run -- demo-run-native "$dir" "$dir/src/main.flow"
finish

# ---------------------------------------------------------------- clean
begin clean_build
manifest cleaner
mkdir -p "$dir/build/sub"
echo x > "$dir/build/sub/file"
run -- clean
finish

begin clean_nothing
run -- clean
finish

if [[ "$mode" == record ]]; then
    exit 0
fi
if [[ -s "$stub_log" ]]; then
    echo "FAIL python was called:"
    sed 's/^/     /' "$stub_log"
    fail=$((fail + 1))
fi
echo "check_pkg_commands: $pass passed, $fail failed"
[[ "$fail" -eq 0 ]]
