#!/usr/bin/env bash
# Backpressure and claim tests for scripts/dispatch_uncovered_jules.sh.
#
# Each case runs the dispatcher in a scratch directory with fake `gh` and
# `jules` commands on PATH, then checks stdout, the decision log and whether
# a session was opened or an issue claimed.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/../../.." && pwd -P)"
DISPATCH="$ROOT/scripts/dispatch_uncovered_jules.sh"

# Build the tool once, outside the per-case timing.
"$ROOT/scripts/tools/build_tool.sh" jules_dispatch >/dev/null

WORK="$(mktemp -d)"
trap 'rm -rf "$WORK"' EXIT

BIN="$WORK/bin"
mkdir -p "$BIN"
cat > "$BIN/gh" <<'EOF'
#!/bin/sh
set -eu
if [ "$1 $2" = "pr list" ]; then
    printf '%s\n' "${FAKE_PRS_JSON:-[]}"
    exit 0
fi
if [ "$1 $2" = "issue list" ]; then
    printf '%s\n' "${FAKE_ISSUES_JSON:-[]}"
    exit 0
fi
if [ "$1 $2" = "run list" ]; then
    printf '%s\n' "${FAKE_MAIN_CI_JSON:-[]}"
    exit 0
fi
if [ "$1 $2" = "issue comment" ]; then
    printf '%s\n' "$*" >> "${FAKE_CLAIM_MARKER}"
    exit 0
fi
echo "unexpected gh invocation: $*" >&2
exit 2
EOF
cat > "$BIN/jules" <<'EOF'
#!/bin/sh
set -eu
if [ "$1 $2 $3" = "remote list --session" ]; then
    printf '%b' "${FAKE_JULES_LIST:-}"
    exit 0
fi
if [ "$1 $2" = "remote new" ]; then
    cat >/dev/null
    : > "${FAKE_NEW_MARKER}"
    printf 'ID: 12345\nURL: https://jules.example/session/12345\n'
    exit 0
fi
echo "unexpected jules invocation: $*" >&2
exit 2
EOF
chmod +x "$BIN/gh" "$BIN/jules"

pass=0
fail=0
CASE=""
DIR=""

# run_case NAME ISSUES_JSON PRS_JSON [VAR=VALUE ...]
run_case() {
    CASE="$1"
    DIR="$WORK/$CASE"
    mkdir -p "$DIR"
    local issues="$2" prs="$3"
    shift 3
    (
        cd "$DIR"
        env PATH="$BIN:$PATH" \
            FAKE_ISSUES_JSON="$issues" FAKE_PRS_JSON="$prs" \
            FAKE_JULES_LIST="" FAKE_MAIN_CI_JSON="[]" \
            FAKE_NEW_MARKER="$DIR/new-session" FAKE_CLAIM_MARKER="$DIR/claim" \
            JULES_DISPATCH_NO_SLEEP=1 JULES_MAX_ACTIVE=8 JULES_MAX_AGENT_PRS=12 \
            "$@" "$DISPATCH" > "$DIR/stdout" 2> "$DIR/stderr"
    ) || { echo "FAIL $CASE: exit $?"; cat "$DIR/stderr"; fail=$((fail + 1)); return 1; }
    touch "$DIR/jules_dispatch_decisions.jsonl"
    return 0
}

check() {
    local what="$1"
    shift
    if "$@"; then
        return 0
    fi
    echo "FAIL $CASE: $what"
    fail=$((fail + 1))
    return 1
}

has_out() { grep -qF -- "$1" "$DIR/stdout"; }
has_decision() { grep -qF -- "$1" "$DIR/jules_dispatch_decisions.jsonl"; }
opened() { [ -e "$DIR/new-session" ]; }
not_opened() { [ ! -e "$DIR/new-session" ]; }
claimed() { [ -e "$DIR/claim" ]; }
done_case() { echo "ok $CASE"; pass=$((pass + 1)); }

issue() { printf '{"number":%s,"title":"%s","body":"repro","labels":[]}' "$1" "${2:-Fix compiler regression}"; }
pr() { printf '{"number":%s,"title":"%s","body":"%s","headRefName":"%s","isDraft":false}' "$1" "$2" "$3" "${4:-jules/work}"; }

# The open agent PR limit applies backpressure.
if run_case agent_pr_limit "[$(issue 42)]" \
        "[$(pr 7 'Other work' 'Created automatically by Jules https://jules.google.com/task/7')]" \
        JULES_MAX_AGENT_PRS=1; then
    check "backpressure message" has_out "Backpressure: agent PR WIP limit reached" &&
    check "no session opened" not_opened &&
    check "backpressure decision" has_decision '"decision":"backpressure"' &&
    done_case
fi

# An open PR for the issue prevents a duplicate dispatch.
if run_case open_pr_for_issue "[$(issue 42)]" \
        "[$(pr 7 'Fix compiler regression' 'Closes #42' 'fix/42')]"; then
    check "no session opened" not_opened &&
    check "deferred decision" has_decision '"decision":"deferred"' &&
    check "overlap reason" has_decision "overlaps open PR #7" &&
    done_case
fi

# Stale local dispatch state is not a permanent claim.
mkdir -p "$WORK/stale_state"
cat > "$WORK/stale_state/jules_dispatch_state.json" <<'EOF'
{"dispatched": {"42": {"issue": 42, "title": "Fix compiler regression", "session": "old", "url": ""}}, "failed": {}}
EOF
if run_case stale_state "[$(issue 42)]" "[]"; then
    check "session opened" opened &&
    check "issue claimed" claimed &&
    check "dispatched decision" has_decision '"decision":"dispatched"' &&
    done_case
fi

# The live session limit stops new work.
if run_case live_session_limit "[$(issue 42)]" "[]" \
        FAKE_JULES_LIST='flooooooooooow/flow issue #99 running\n' JULES_MAX_ACTIVE=1; then
    check "backpressure message" has_out "Backpressure: active Jules session limit reached" &&
    check "no session opened" not_opened &&
    check "backpressure decision" has_decision '"decision":"backpressure"' &&
    done_case
fi

# Red main CI pauses cleanup work and keeps repair work.
if run_case red_main_ci "[$(issue 41 'Cleanup unused imports'),$(issue 42 'Fix CI regression in compiler')]" "[]" \
        FAKE_MAIN_CI_JSON='[{"status": "completed", "conclusion": "failure"}]'; then
    check "backpressure message" has_out "Backpressure: main CI is red" &&
    check "repair session opened" opened &&
    check "cleanup deferred" has_decision '"issue":41,"decision":"deferred"' &&
    check "pause reason" has_decision "main CI is red; low-priority work paused" &&
    check "repair dispatched" has_decision '"issue":42,"decision":"dispatched"' &&
    done_case
fi

echo "jules_dispatch tests: pass=$pass fail=$fail"
[ "$fail" -eq 0 ]
