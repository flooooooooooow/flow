# Shared helpers for the shell tests in tests/scripts. Source this file,
# define one function per check, run each with t_check, and end with t_done.
#
# A check runs in a subshell under `set -e`, so the first failing command
# or assertion fails it. Exit status 77 (t_skip) marks it skipped.
#
#   t_check NAME FUNCTION [ARGS...]   prints PASS/FAIL/SKIP <file>/<NAME>
#   t_skip REASON                      skip the current check
#   t_need CMD...                      skip unless every CMD is on PATH
#   t_run CMD...                       run CMD; sets T_RC, T_OUT and T_ERR
#                                      (files holding stdout and stderr)
#   a_eq ACTUAL EXPECTED [WHAT]        string equality
#   a_contains HAYSTACK NEEDLE         substring
#   a_not_contains HAYSTACK NEEDLE
#   a_file_is FILE TEXT                file holds exactly TEXT (bytes)
#   a_file_contains FILE NEEDLE
#   a_exists PATH
#   a_true WHAT CMD...                 CMD succeeds
#
# Assertions print what they expected and return 1.

set -uo pipefail

T_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$T_ROOT"
T_NAME="$(basename "$0" .sh)"
T_WORK="$(mktemp -d "${TMPDIR:-/tmp}/flow-script-tests.XXXXXX")"
trap 'rm -rf "$T_WORK"' EXIT
T_PASS=0
T_FAIL=0
T_SKIP=0
T_SEQ=0

t_check() {
    local name="$1"
    shift
    T_SEQ=$((T_SEQ + 1))
    # Each check gets its own scratch directory, like pytest's tmp_path.
    T_TMP="$T_WORK/check$T_SEQ"
    mkdir -p "$T_TMP"
    local log="$T_TMP/.log"
    ( set -e; "$@" ) > "$log" 2>&1
    local rc=$?
    if [[ "$rc" -eq 0 ]]; then
        echo "PASS $T_NAME/$name"
        T_PASS=$((T_PASS + 1))
    elif [[ "$rc" -eq 77 ]]; then
        echo "SKIP $T_NAME/$name ($(tail -n 1 "$log"))"
        T_SKIP=$((T_SKIP + 1))
    else
        echo "FAIL $T_NAME/$name"
        tail -n 40 "$log" | sed 's/^/    /'
        T_FAIL=$((T_FAIL + 1))
    fi
}

t_skip() {
    echo "$1"
    exit 77
}

t_need() {
    local cmd
    for cmd in "$@"; do
        command -v "$cmd" > /dev/null 2>&1 || t_skip "requires $cmd"
    done
}

# Skip unless a C compiler (cc or clang) is on PATH.
t_need_cc() {
    command -v cc > /dev/null 2>&1 || command -v clang > /dev/null 2>&1 \
        || t_skip "no C compiler"
}

t_run() {
    T_OUT="$T_TMP/.out.$RANDOM"
    T_ERR="$T_TMP/.err.$RANDOM"
    set +e
    "$@" > "$T_OUT" 2> "$T_ERR"
    T_RC=$?
    set -e
}

a_eq() {
    if [[ "$1" != "$2" ]]; then
        echo "expected ${3:-value} to be [$2], got [$1]"
        return 1
    fi
}

a_contains() {
    if [[ "$1" != *"$2"* ]]; then
        echo "expected to find [$2] in:"
        printf '%s\n' "$1" | head -n 20
        return 1
    fi
}

a_not_contains() {
    if [[ "$1" == *"$2"* ]]; then
        echo "did not expect [$2] in:"
        printf '%s\n' "$1" | head -n 20
        return 1
    fi
}

a_file_is() {
    if ! printf '%s' "$2" | cmp -s - "$1"; then
        echo "expected $1 to hold exactly:"
        printf '%s' "$2" | od -c | head -n 10
        echo "it holds:"
        od -c "$1" | head -n 10
        return 1
    fi
}

a_file_contains() {
    if ! grep -qF -- "$2" "$1"; then
        echo "expected to find [$2] in $1:"
        head -n 20 "$1"
        return 1
    fi
}

a_exists() {
    if [[ ! -e "$1" ]]; then
        echo "expected $1 to exist"
        return 1
    fi
}

a_true() {
    local what="$1"
    shift
    if ! "$@"; then
        echo "expected: $what"
        return 1
    fi
}

t_done() {
    echo "$T_NAME: $T_PASS passed, $T_FAIL failed, $T_SKIP skipped"
    [[ "$T_FAIL" -eq 0 ]]
    exit $?
}
