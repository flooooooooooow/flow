#!/usr/bin/env bash
# Sync open ROADMAP.md items to GitHub issues ([roadmap] label) and to
# docs/project/issues-checklist.md.
#
# The logic is the Flow program in scripts/tools/roadmap_sync. Flow cannot
# run gh, so this shim runs it in phases: the program works out what to do
# and writes the gh calls to build/roadmap-sync/plan.txt, the shim makes the
# calls, and the program then rewrites the checklist from the results.
#
# Usage:
#   ./scripts/sync_roadmap.sh [--roadmap ROADMAP.md]
#       [--checklist docs/project/issues-checklist.md]
#       [--repo owner/name] [--dry-run] [--verbose]
#
# Requires: gh (authenticated).

set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

BIN="$(scripts/tools/build_tool.sh roadmap_sync)"
WORK=build/roadmap-sync
rm -rf "$WORK"
mkdir -p "$WORK"

LABEL=roadmap
LABEL_COLOR=5319E7
LABEL_DESC="Open ROADMAP.md item synced by scripts/sync_roadmap.sh"

# Phase 1: check the arguments and files, and learn the repository.
repo="$("$BIN" --phase args "$@")"

# Every roadmap issue in one call, keyed later by its ROADMAP-SYNC marker.
status=0
gh issue list --repo "$repo" --label "$LABEL" --state all --limit 500 \
  --json number,title,body >"$WORK/issues.json" 2>"$WORK/issues.err" || status=$?
echo "$status" >"$WORK/issues.status"

# Phase 2: report, and plan the GitHub changes.
"$BIN" --phase plan "$@"
if [[ "$(head -n 1 "$WORK/plan.txt")" == "dry-run" ]]; then
  exit 0
fi

verbose=0
if grep -qx verbose "$WORK/plan.txt"; then
  verbose=1
fi

gh label create "$LABEL" --repo "$repo" --color "$LABEL_COLOR" \
  --description "$LABEL_DESC" >/dev/null 2>&1 || true

# Run gh quietly, as the Python version did; show its stderr only on failure.
run_gh() {
  local err
  if ! err="$(gh "$@" 2>&1 >/dev/null)"; then
    printf '%s\n' "$err" >&2
    exit 1
  fi
}

: >"$WORK/created.txt"
while IFS=$'\t' read -r kind a b c d; do
  case "$kind" in
    adopt)
      # a=number b=new slug c=old slug d=title
      run_gh issue edit "$a" --repo "$repo" --title "[roadmap] $d"
      body="$(gh issue view "$a" --repo "$repo" --json body --jq .body 2>"$WORK/view.err")" || {
        cat "$WORK/view.err" >&2
        exit 1
      }
      body="$(printf '%s' "$body" | sed -E "s/ROADMAP-SYNC: [a-z0-9-]+/ROADMAP-SYNC: $b/g")"
      run_gh issue edit "$a" --repo "$repo" --body "$body"
      if [[ "$verbose" -eq 1 ]]; then
        echo "adopted #$a as '$d' (was slug '$c')"
      fi
      ;;
    create)
      # a=slug b=body file c=title
      out="$(gh issue create --repo "$repo" --label "$LABEL" \
        --title "[roadmap] $c" --body-file "$b" 2>"$WORK/create.err")" || {
        cat "$WORK/create.err" >&2
        exit 1
      }
      number=0
      if [[ "$out" =~ issues/([0-9]+) ]]; then
        number="${BASH_REMATCH[1]}"
      fi
      if [[ "$verbose" -eq 1 ]]; then
        echo "created #$number: $c"
      fi
      printf '%s\t%s\t%s\n' "$a" "$number" "$out" >>"$WORK/created.txt"
      ;;
    close)
      if [[ "$verbose" -eq 1 ]]; then
        echo "closing #$a"
      fi
      run_gh issue close "$a" --repo "$repo"
      ;;
  esac
done <"$WORK/plan.txt"

# Phase 3: rewrite the checklist with the new issue numbers.
"$BIN" --phase apply "$@"
