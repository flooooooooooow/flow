#!/usr/bin/env bash
# Refresh README.md and docs/generated/repository-stats.json.
#
# The counter is the Flow program in scripts/tools/repo_stats. It runs git
# itself through std.process; this script only builds it and runs it with a
# time limit.
#
# Usage:
#   ./scripts/update_repo_stats.sh
#   ./scripts/update_repo_stats.sh --check

set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

BIN="$(scripts/tools/build_tool.sh repo_stats)"

# Bound the runtime so a stuck binary cannot block CI forever. The kill has
# to be SIGKILL: a process blocked in a syscall can sit on a catchable
# signal indefinitely.
timeout_s="${FLOW_STATS_TIMEOUT:-90}"
if command -v timeout >/dev/null 2>&1; then
  exec timeout -k 5 "$timeout_s" "$BIN" "$@"
fi

# No coreutils `timeout` (typically macOS): poll instead of waiting, so a
# process that never reaps cannot block this script either.
"$BIN" "$@" &
pid=$!
waited=0
while kill -0 "$pid" 2>/dev/null; do
  if [[ "$waited" -ge "$timeout_s" ]]; then
    kill -9 "$pid" 2>/dev/null || true
    exit 124
  fi
  sleep 1
  waited=$((waited + 1))
done
rc=0
wait "$pid" || rc=$?
exit "$rc"
