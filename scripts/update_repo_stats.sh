#!/usr/bin/env bash
# Refresh README.md and docs/generated/repository-stats.json.
#
# The counter is the Flow program in scripts/tools/repo_stats. Flow cannot
# spawn processes yet, so git runs here and leaves its output in
# build/repo-stats/ for the Flow program to read.
#
# Usage:
#   ./scripts/update_repo_stats.sh
#   ./scripts/update_repo_stats.sh --check

set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

MODE="write"
if [[ "${1:-}" == "--check" ]]; then
  MODE="check"
fi

mkdir -p build/repo-stats docs/generated

# Attribute stats to the last commit that actually changed the tree, not to
# this job's own commit. Bounded so a shallow clone, or a run of stats-only
# commits, cannot walk past the grafted root.
STATS_SUBJECT='docs: refresh repository statistics [skip ci]'
REV="HEAD"
for _ in 1 2 3 4 5; do
  subject="$(git show -s --format=%s "$REV" 2>/dev/null || true)"
  [[ "$subject" == "$STATS_SUBJECT" ]] || break
  git rev-parse --verify --quiet "${REV}^" >/dev/null || break
  REV="${REV}^"
done

{
  echo "commit=$(git rev-parse --short=12 "$REV")"
  echo "generated_at=$(git show -s --format=%cI "$REV")"
} > build/repo-stats/meta.txt

git ls-files > build/repo-stats/files.txt
printf '%s\n' "$MODE" > build/repo-stats/mode.txt

BIN="$(scripts/tools/build_tool.sh repo_stats)"

# Bound the runtime so a stuck binary cannot block CI forever. The kill has
# to be SIGKILL: a process blocked in a syscall can sit on a catchable
# signal indefinitely.
timeout_s="${FLOW_STATS_TIMEOUT:-90}"
if command -v timeout >/dev/null 2>&1; then
  exec timeout -k 5 "$timeout_s" "$BIN"
fi

# No coreutils `timeout` (typically macOS): poll instead of waiting, so a
# process that never reaps cannot block this script either.
"$BIN" &
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
