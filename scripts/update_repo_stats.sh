#!/usr/bin/env bash
# Refresh README.md and docs/generated/repository-stats.json.
#
# The counter of record is the Flow program in scripts/tools/repo_stats.
# Flow cannot spawn processes yet, so git runs here and leaves its output
# in build/repo-stats/ for the Flow program to read.
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

FLOW_SRC="scripts/tools/repo_stats/main.flow"
FLOW_C="build/repo-stats/main.c"
FLOW_BIN="build/repo-stats/repo_stats"

PY="${PYTHON:-}"
if [[ -z "$PY" ]]; then
  if /usr/bin/python3 -c 'import numpy' 2>/dev/null; then
    PY=/usr/bin/python3
  else
    PY=python3
  fi
fi

build_flow() {
  if [[ -x "$FLOW_BIN" && "$FLOW_BIN" -nt "$FLOW_SRC" ]]; then
    return 0
  fi
  PYTHONPATH=src "$PY" -m flow.transpiler "$FLOW_SRC" --c -o "$FLOW_C"
  # No GPU or graphics runtime needed for this tool, so link it directly.
  clang -O2 -Iruntime "$FLOW_C" -o "$FLOW_BIN"
}

run_flow() {
  build_flow
  # Bound the runtime so a stuck binary cannot block CI forever. The kill has
  # to be SIGKILL: a process blocked in a syscall can sit on a catchable
  # signal indefinitely, which is exactly how this hangs in practice.
  local timeout_s="${FLOW_STATS_TIMEOUT:-90}"
  if command -v timeout >/dev/null 2>&1; then
    timeout -k 5 "$timeout_s" "$FLOW_BIN"
    return $?
  fi

  # No coreutils `timeout` (typically macOS): poll instead of waiting, so a
  # process that never reaps cannot block this script either.
  "$FLOW_BIN" &
  local pid=$!
  local waited=0
  while kill -0 "$pid" 2>/dev/null; do
    if [[ "$waited" -ge "$timeout_s" ]]; then
      kill -9 "$pid" 2>/dev/null || true
      return 124
    fi
    sleep 1
    waited=$((waited + 1))
  done
  local rc=0
  wait "$pid" || rc=$?
  return "$rc"
}

run_python() {
  echo "repo_stats: Flow path unavailable — using the Python reference" >&2
  if [[ "$MODE" == "check" ]]; then
    "$PY" scripts/update_repo_stats.py --check
  else
    "$PY" scripts/update_repo_stats.py
  fi
}

if run_flow; then
  # Nothing else proves the Flow counter agrees with the reference, so diff
  # them on every run. A silent divergence in published numbers would be
  # worse than a loud failure.
  if "$PY" scripts/update_repo_stats.py --check >/dev/null 2>&1; then
    exit 0
  fi
  echo "repo_stats: Flow output disagrees with the Python reference:" >&2
  "$PY" scripts/update_repo_stats.py --check >&2 || true
  if [[ "$MODE" == "write" ]]; then
    echo "repo_stats: rewriting with Python so the numbers stay correct" >&2
    "$PY" scripts/update_repo_stats.py >&2
  fi
  exit 1
fi

run_python
