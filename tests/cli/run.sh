#!/usr/bin/env bash
# Golden tests for the `flow` command line.
#
# Each case in tests/cli/cases.sh runs `flow` once and records what it did:
# stdout, stderr, the exit code and, for cases that write files, which files
# exist afterwards (with a checksum for text). tests/cli/goldens/ holds the
# behaviour of the bash driver the Flow CLI replaced, so this is the parity
# gate for tools/flow_cli.
#
# Paths that change between machines and runs are rewritten before the
# comparison: the repository root, the scratch directory, mktemp names.
#
# Usage: tests/cli/run.sh [--update] [name...]
#   FLOW_CLI=path  the command under test (default: ./flow)
set -uo pipefail

ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
ROOT_P="$(cd "$ROOT" && pwd -P)"
cd "$ROOT"
# Goldens are per OS (clang, ld and the tools on PATH differ): goldens/<os>.
OS="$(uname -s | tr "[:upper:]" "[:lower:]")"
GOLD="$ROOT/tests/cli/goldens/$OS"
FIX="$ROOT/tests/cli/fixtures"
FLOW="${FLOW_CLI:-$ROOT/flow}"

UPDATE=0
if [ "${1:-}" = "--update" ]; then
    UPDATE=1
    shift
fi
ONLY=" $* "

if [ "$UPDATE" -eq 0 ] && [ ! -d "$GOLD" ]; then
    echo "tests/cli: no goldens for $OS (tests/cli/goldens/$OS); record them with --update"
    exit 1
fi
mkdir -p "$GOLD"

work="$(mktemp -d "${TMPDIR:-/tmp}/flow-cli-tests.XXXXXX")"
work_p="$(cd "$work" && pwd -P)"
trap 'rm -rf "$work"' EXIT
tmp_root="${TMPDIR:-/tmp}"
tmp_root="${tmp_root%/}"

pass=0
fail=0
failed=()

normalize() {
    sed -e "s#$work_p#<WORK>#g" -e "s#$work#<WORK>#g" \
        -e "s#$ROOT_P#<ROOT>#g" -e "s#$ROOT#<ROOT>#g" \
        -e "s#$tmp_root#<TMP>#g" -e "s#/private<TMP>#<TMP>#g" \
        -e 's#build/run\.[A-Za-z0-9]\{6\}#build/run.XXXXXX#g' \
        -e 's#<TMP>/[A-Za-z_.-]*[.]\([A-Za-z0-9]\{6,\}\)#<TMP>/MKTEMP#g' \
        -e 's#<TMP>/tmp\.[A-Za-z0-9]*#<TMP>/MKTEMP#g' \
        -e 's#<TMP>/\([A-Za-z0-9_]*\)-[0-9a-f]\{6\}\.o#<TMP>/\1-XXXXXX.o#g' \
        -e 's#flowc_runtime/[0-9]*-[0-9]*#flowc_runtime/KEY#g' \
        -e 's#\("[a-z_]*_s": \)[0-9.]*#\1N#g'
}

compare() {
    local name="$1" kind="$2" actual="$3"
    local expected="$GOLD/$name.$kind"
    if [ "$UPDATE" -eq 1 ]; then
        cp "$actual" "$expected"
        return 0
    fi
    if [ ! -f "$expected" ]; then
        echo "  missing golden $name.$kind"
        return 1
    fi
    if ! cmp -s "$expected" "$actual"; then
        echo "  $kind differs:"
        diff -u "$expected" "$actual" | sed 's/^/    /' | head -40
        return 1
    fi
    return 0
}

# t NAME [cwd=root|proj|empty] [env=K=V]... [files=a,b] [stdin=FILE] -- ARGS...
t() {
    local name="$1"
    shift
    if [ "$ONLY" != "  " ] && [[ "$ONLY" != *" $name "* ]]; then
        return 0
    fi
    local cwd=root files="" stdin=/dev/null
    local -a envs=()
    while [ $# -gt 0 ] && [ "$1" != "--" ]; do
        case "$1" in
            cwd=*) cwd="${1#cwd=}" ;;
            env=*) envs+=("${1#env=}") ;;
            files=*) files="${1#files=}" ;;
            stdin=*) stdin="$ROOT/${1#stdin=}" ;;
        esac
        shift
    done
    shift
    local dir="$ROOT"
    case "$cwd" in
        proj)
            dir="$work/$name"
            mkdir -p "$dir"
            cp -R "$FIX/proj/." "$dir/"
            ;;
        empty)
            dir="$work/$name"
            mkdir -p "$dir"
            ;;
    esac
    # @ROOT in an argument is the repository root.
    local -a argv=()
    local a
    for a in "$@"; do
        argv+=("${a//@ROOT/$ROOT}")
    done
    local out="$work/$name.out" err="$work/$name.err" code="$work/$name.code"
    local rc=0
    (cd "$dir" && env ${envs[@]+"${envs[@]}"} "$FLOW" ${argv[@]+"${argv[@]}"} <"$stdin" >"$out.raw" 2>"$err.raw") || rc=$?
    normalize <"$out.raw" >"$out"
    normalize <"$err.raw" >"$err"
    echo "$rc" >"$code"
    local ok=0
    compare "$name" out "$out" || ok=1
    compare "$name" err "$err" || ok=1
    compare "$name" code "$code" || ok=1
    if [ -n "$files" ]; then
        local manifest="$work/$name.files" f
        : >"$manifest"
        IFS=',' read -ra flist <<<"$files"
        for f in "${flist[@]}"; do
            if [ ! -e "$dir/$f" ]; then
                echo "$f: missing" >>"$manifest"
            elif [ -d "$dir/$f" ]; then
                echo "$f: directory" >>"$manifest"
            else
                case "$f" in
                    *.c|*.flow|*.toml|*.mlir|*.metal|*.wgsl|*.lock|*.json|*.txt|*.md|*.ll)
                        echo "$f: $(normalize <"$dir/$f" | cksum | awk '{print $1 "-" $2}')" >>"$manifest" ;;
                    *) echo "$f: present" >>"$manifest" ;;
                esac
            fi
        done
        compare "$name" files "$manifest" || ok=1
    fi
    if [ "$ok" -eq 0 ]; then
        pass=$((pass + 1))
        [ "$UPDATE" -eq 1 ] && echo "updated $name" || echo "PASS $name"
    else
        fail=$((fail + 1))
        failed+=("$name")
        echo "FAIL $name"
    fi
}

# Warm the caches first, so no case sees one-time build chatter (flowc from
# the bootstrap C, the Flow tools, the runtime archive).
"$FLOW" compile "tests/cli/fixtures/hello.flow" >/dev/null 2>&1 || true
for tool in check lsp; do
    "$FLOW" "$tool" --build >/dev/null 2>&1 || true
done

# shellcheck source=tests/cli/cases.sh
source "$ROOT/tests/cli/cases.sh"

echo "tests/cli: $pass passed, $fail failed"
if [ "$fail" -gt 0 ]; then
    echo "failed: ${failed[*]}"
    exit 1
fi
