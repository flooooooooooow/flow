#!/usr/bin/env bash
# Parity check: the Flow package manager (compiler/src/pkg.flow) against the
# Python one it replaced (src/flow/package.py at PARITY_REF).
#
# Every case runs twice in fresh copies of the same project, once per
# implementation, and compares stdout, the exit status, flow.toml, flow.lock
# and flow_packages/ (file list, contents and modes).
#
# Needs python3 and git for the reference side only. Cases cover every
# package in registry/packages, path/git/stdlib dependencies, a registry
# override with several versions, and the error paths (unknown package, bad
# version constraint, missing path, bad git ref).
#
# Usage: scripts/check_pkg_parity.sh
set -uo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd -P)"
cd "$ROOT"

# The last commit whose src/flow/package.py still held the Python installer.
PARITY_REF="${PARITY_REF:-660ff30df57291a5734e732e0c7fd345158eff32}"

work="$(mktemp -d "${TMPDIR:-/tmp}/flow-pkg-parity.XXXXXX")"
work="$(cd "$work" && pwd -P)"
trap 'rm -rf "$work"' EXIT

# --- reference: the Python package manager, as it was --------------------
ref="$work/ref"
mkdir -p "$ref/src/flow"
: > "$ref/src/flow/__init__.py"
for f in package.py registry.py toml_compat.py project_config.py; do
    git show "$PARITY_REF:src/flow/$f" > "$ref/src/flow/$f" || {
        echo "check_pkg_parity: cannot read $f at $PARITY_REF"; exit 1; }
done
ln -s "$ROOT/lib" "$ref/lib"
ln -s "$ROOT/registry" "$ref/registry"

# --- native: the Flow package manager ------------------------------------
# Any package command builds the tool (build/tools/flow_pkg/flow_pkg).
(cd "$work" && bash "$ROOT/flow-driver" info hello_lib >/dev/null 2>&1)
tool="$ROOT/build/tools/flow_pkg/flow_pkg"
if [ ! -x "$tool" ]; then
    echo "check_pkg_parity: could not build the Flow package tool"
    exit 1
fi

run_ref() {
    PYTHONPATH="$ref/src" python3 -m flow.package "$@"
}
run_native() {
    FLOW_REPO_ROOT="$ROOT" "$tool" "$@"
}

pass=0
fail=0

# Snapshot of a project: manifest, lock and the installed tree.
snapshot() {
    local dir="$1"
    (
        cd "$dir" || exit 1
        echo "== flow.toml"
        [ -f flow.toml ] && cat flow.toml
        echo "== flow.lock"
        [ -f flow.lock ] && cat flow.lock
        echo "== flow_packages"
        if [ -d flow_packages ]; then
            find flow_packages -print | LC_ALL=C sort | while IFS= read -r p; do
                if [ "$(basename "$p")" = ".git" ] && [ -d "$p" ]; then
                    # A clone's own metadata holds timestamps; compare the
                    # checked-out commit instead of the bytes.
                    echo "G $p HEAD=$(git -C "$(dirname "$p")" rev-parse HEAD 2>/dev/null)"
                    echo "G $p files=$(find "$p" -type f | wc -l | tr -d ' ')"
                elif case "$p" in */.git/*) true ;; *) false ;; esac; then
                    :
                elif [ -L "$p" ]; then
                    echo "L $p -> $(readlink "$p")"
                elif [ -d "$p" ]; then
                    echo "D $p"
                else
                    mode="$(ls -l "$p" | cut -c1-10)"
                    sum="$(cksum < "$p")"
                    echo "F $p $mode $sum"
                fi
            done
        fi
    )
}

# case NAME SETUP_FN ARGS...: SETUP_FN builds the project in the directory
# given as its argument; ARGS go to both package managers.
case_run() {
    local name="$1"
    local setup="$2"
    shift 2
    local a="$work/cases/$name/python" b="$work/cases/$name/flow"
    mkdir -p "$a" "$b"
    (cd "$a" && "$setup" "$a") >/dev/null 2>&1
    (cd "$b" && "$setup" "$b") >/dev/null 2>&1
    local ra=0 rb=0
    (cd "$a" && run_ref "$@") > "$a.out" 2>"$a.err" || ra=$?
    (cd "$b" && run_native "$@") > "$b.out" 2>"$b.err" || rb=$?
    # Paths inside the output name each copy's own directory.
    sed "s#$a#<proj>#g" "$a.out" > "$a.out.n"
    sed "s#$b#<proj>#g" "$b.out" > "$b.out.n"
    snapshot "$a" | sed "s#$a#<proj>#g" > "$a.snap"
    snapshot "$b" | sed "s#$b#<proj>#g" > "$b.snap"
    local ok=1
    if [ "$ra" != "$rb" ]; then
        echo "FAIL $name: exit python=$ra flow=$rb"
        ok=0
    fi
    if ! cmp -s "$a.out.n" "$b.out.n"; then
        echo "FAIL $name: stdout differs"
        diff "$a.out.n" "$b.out.n" | head -20
        ok=0
    fi
    if ! cmp -s "$a.snap" "$b.snap"; then
        echo "FAIL $name: project state differs"
        diff "$a.snap" "$b.snap" | head -30
        ok=0
    fi
    if [ "$ok" = 1 ]; then
        echo "PASS $name (exit $ra)"
        pass=$((pass + 1))
    else
        fail=$((fail + 1))
    fi
}

manifest() {
    # manifest NAME DEP_LINES...
    local name="$1"
    shift
    {
        echo "[package]"
        echo "name = \"$name\""
        echo "version = \"0.1.0\""
        echo "entry = \"src/main.flow\""
        echo
        echo "[dependencies]"
        for line in "$@"; do
            echo "$line"
        done
        echo
        echo "[dev-dependencies]"
    } > flow.toml
    mkdir -p src
    printf 'function main() -> i32 {\n    return 0\n}\n' > src/main.flow
}

setup_empty() { manifest app; }

# --- every registry package: install, add, sync, pinned requirement ------
for dir in registry/packages/*/; do
    pkg="$(basename "$dir")"
    eval "setup_dep_$pkg() { manifest app '$pkg = \"0.1.0\"'; }"
    eval "setup_caret_$pkg() { manifest app '$pkg = \"^0.1\"'; }"
    case_run "install-$pkg" "setup_dep_$pkg" install
    case_run "sync-$pkg" "setup_caret_$pkg" sync --program src/main.flow
    case_run "add-$pkg" setup_empty add "$pkg"
    case_run "add-at-$pkg" setup_empty add "$pkg@^0.1.0"
done
setup_verify() { manifest app 'flow-verify = "*"'; }
case_run "install-flow-verify" setup_verify install

# --- version requirements and errors --------------------------------------
case_run "add-latest" setup_empty add json@latest
case_run "add-ge" setup_empty add json --version ">=0.1.0"
case_run "add-exact-eq" setup_empty add json --version "==0.1.0"
case_run "add-unknown" setup_empty add no_such_package
case_run "add-bad-constraint" setup_empty add json@^9.0
case_run "add-garbage-constraint" setup_empty add "json@not.a.version"
case_run "add-twice" setup_dep_json add json
setup_unknown() { manifest app 'no_such_package = "1.0.0"'; }
case_run "install-unknown" setup_unknown install
case_run "sync-unknown" setup_unknown sync --program src/main.flow
setup_bad_version() { manifest app 'json = "2.0.0"'; }
case_run "install-bad-version" setup_bad_version install
setup_garbage_version() { manifest app 'json = "^abc"'; }
case_run "install-garbage-version" setup_garbage_version install
setup_partial() { manifest app 'json = "0.1.0"' 'nope = "1.0.0"' 'toml = "*"'; }
case_run "install-partial-failure" setup_partial install
case_run "add-no-manifest" true add json
case_run "install-no-manifest" true install
case_run "add-usage" setup_empty add
case_run "info-missing-arg" setup_empty info

# --- flow.lock handling ----------------------------------------------------
setup_locked() {
    manifest app 'json = "0.1.0"' 'toml = "0.1.0"'
    cat > flow.lock <<EOF
{
  "version": 1,
  "packages": {
    "zzz_other": {
      "version": "9.9.9",
      "source": "registry"
    },
    "toml": {
      "version": "0.1.0",
      "source": "registry",
      "resolved": {
        "path": "$ROOT/registry/packages/toml"
      }
    }
  },
  "extra": "café"
}
EOF
}
case_run "install-existing-lock" setup_locked install
setup_bad_lock() { manifest app 'json = "0.1.0"'; echo '{ not json' > flow.lock; }
case_run "install-malformed-lock" setup_bad_lock install
setup_synced() {
    setup_locked
    mkdir -p flow_packages/json flow_packages/toml
}
case_run "sync-already-installed" setup_synced sync --program src/main.flow

# --- path, stdlib and local-file dependencies -----------------------------
make_lib() {
    mkdir -p "$1/src" "$1/build" "$1/.git" "$1/src/__pycache__" "$1/nested/build"
    printf 'export function f() -> i32 {\n    return 1\n}\n' > "$1/src/lib.flow"
    echo "x" > "$1/build/out.o"
    echo "x" > "$1/.git/HEAD"
    echo "x" > "$1/src/__pycache__/m.pyc"
    echo "x" > "$1/src/stale.pyc"
    echo "x" > "$1/nested/build/o"
    echo "keep" > "$1/nested/keep.txt"
    chmod 755 "$1/nested/keep.txt"
}
setup_path() {
    make_lib ../shared_lib_$$
    manifest app 'mylib = { path = "../shared_lib_'$$'" }'
}
case_run "install-path" setup_path install
setup_path_file() {
    printf 'export function g() -> i32 {\n    return 2\n}\n' > ../single_$$.flow
    manifest app 'single = { path = "../single_'$$'.flow" }'
}
case_run "install-path-file" setup_path_file install
setup_path_missing() { manifest app 'gone = { path = "../does_not_exist" }'; }
case_run "install-path-missing" setup_path_missing install
setup_add_path() { make_lib vendor/lib2; manifest app; }
case_run "add-path" setup_add_path add --path vendor/lib2 --name lib2
setup_stdlib() { manifest app 'collections = "*"'; }
case_run "install-stdlib" setup_stdlib install
case_run "add-stdlib" setup_empty add collections
setup_local_file() { manifest app 'helper = "1.0.0"'; echo "# local" > helper.flow; }
case_run "install-local-file" setup_local_file install
setup_unsupported() { manifest app 'odd = { version = "1.0" }'; }
case_run "install-unsupported-spec" setup_unsupported install

# --- git dependencies (a local repository over file://) -------------------
gitrepo="$work/gitsrc/mylib"
mkdir -p "$gitrepo/pkgs/sub/src"
(
    cd "$gitrepo" &&
    git init -q &&
    git config user.email parity@example.invalid &&
    git config user.name parity &&
    printf 'export function f() -> i32 {\n    return 1\n}\n' > lib.flow &&
    printf 'export function s() -> i32 {\n    return 2\n}\n' > pkgs/sub/src/lib.flow &&
    git add -A && git commit -q -m one && git tag v1 &&
    echo "# two" >> lib.flow && git commit -q -am two && git branch -q stable
) >/dev/null 2>&1
first_sha="$(git -C "$gitrepo" rev-list --max-parents=0 HEAD)"
setup_git_tag() { manifest app "mylib = { git = \"file://$gitrepo\", tag = \"v1\" }"; }
case_run "install-git-tag" setup_git_tag install
setup_git_rev() { manifest app "mylib = { git = \"file://$gitrepo\", rev = \"$first_sha\" }"; }
case_run "install-git-rev" setup_git_rev install
setup_git_subdir() { manifest app "sub = { git = \"file://$gitrepo\", branch = \"stable\", subdir = \"pkgs/sub\" }"; }
case_run "install-git-subdir" setup_git_subdir install
setup_git_bad_subdir() { manifest app "sub = { git = \"file://$gitrepo\", subdir = \"nope\" }"; }
case_run "install-git-bad-subdir" setup_git_bad_subdir install
setup_git_bad_tag() { manifest app "mylib = { git = \"file://$gitrepo\", tag = \"v404\" }"; }
case_run "install-git-bad-tag" setup_git_bad_tag install
case_run "add-git-url" setup_empty add "git+file://$gitrepo.git#main" --tag v1
case_run "add-git-flag" setup_empty add --git "file://$gitrepo" --name mine --branch stable --subdir pkgs/sub

# --- registry override: several versions, yanked, git sources -------------
index="$work/index.json"
cat > "$index" <<EOF
{
  "name": "parity-index",
  "crates": {
    "multi": {
      "description": "Several versions",
      "versions": [
        {"version": "1.2.0", "path": "$ROOT/registry/packages/json"},
        {"version": "1.10.0", "yanked": true, "path": "$ROOT/registry/packages/toml"},
        {"version": "1.3.0", "path": "registry/packages/mathkit"},
        {"version": "v2.0.0-beta", "path": "registry/packages/strings"},
        {"version": "0.4.1", "path": "registry/packages/log"}
      ]
    },
    "viagit": {
      "description": "From git",
      "homepage": "https://example.invalid/viagit",
      "versions": [
        {"version": "0.1.0", "git": "file://$gitrepo", "tag": "v1"}
      ]
    }
  }
}
EOF
export FLOW_REGISTRY_PATH="$index"
for req in '*' '^1.2' '^1' '>=1.2.5' '==1.2' '1.3.0' '^0.4' '^0.4.2' '2' '1.10.0' 'v2' ' 1.3.0 '; do
    slug="$(printf '%s' "$req" | tr -c 'A-Za-z0-9.' '_')"
    eval "setup_multi_$slug() { manifest app 'multi = \"$req\"'; }"
    case_run "override-install-$slug" "setup_multi_$slug" install
done
case_run "override-add" setup_empty add multi
case_run "override-add-caret" setup_empty add multi@^0.4
case_run "override-add-git" setup_empty add viagit
case_run "override-search" setup_empty search
case_run "override-info" setup_empty info multi
unset FLOW_REGISTRY_PATH

# --- search / info against the bundled index -------------------------------
case_run "search-all" setup_empty search
case_run "search-json" setup_empty search json
case_run "search-pure" setup_empty search pure
case_run "search-none" setup_empty search zzzz_nothing
case_run "info-json" setup_empty info json
case_run "info-unknown" setup_empty info nope

echo
echo "parity: pass=$pass fail=$fail"
[ "$fail" -eq 0 ]
