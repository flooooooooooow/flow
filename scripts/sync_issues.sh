#!/usr/bin/env bash
set -euo pipefail

# Bi-directional sync between docs/project/issues-checklist.md and GitHub issues.
# - If an issue is closed on GitHub, mark [x] locally.
# - If an issue is [x] locally and open on GitHub, close it (optionally comment).
#
# Usage:
#   scripts/sync_issues.sh [--repo owner/name] [--file path] [--comment "text"] [--dry-run]
#
# Requires: gh (authenticated), jq

REPO="flooooooooooow/flow"
FILE="docs/project/issues-checklist.md"
COMMENT=""
DRY_RUN=0
VERBOSE=0

while [[ $# -gt 0 ]]; do
  case "$1" in
    --repo)
      REPO="$2"
      shift 2
      ;;
    --file)
      FILE="$2"
      shift 2
      ;;
    --comment)
      COMMENT="$2"
      shift 2
      ;;
    --dry-run)
      DRY_RUN=1
      shift
      ;;
    --verbose)
      VERBOSE=1
      shift
      ;;
    --debug)
      VERBOSE=1
      set -x
      shift
      ;;
    *)
      echo "Unknown arg: $1" >&2
      exit 1
      ;;
  esac
done

if ! command -v gh >/dev/null 2>&1; then
  echo "gh not found. Install GitHub CLI first." >&2
  exit 1
fi

if ! command -v jq >/dev/null 2>&1; then
  echo "jq not found. Install jq first." >&2
  exit 1
fi

if [[ ! -f "$FILE" ]]; then
  echo "Checklist file not found: $FILE" >&2
  exit 1
fi

tmp="$(mktemp)"

get_issue_number() {
  printf '%s\n' "$1" | sed -n 's/^- \[[ xX]\] #\([0-9][0-9]*\) .*/\1/p'
}

is_checked_line() {
  case "$1" in
    "- [x]"*|"- [X]"*) return 0 ;;
    *) return 1 ;;
  esac
}

while IFS= read -r line; do
  num="$(get_issue_number "$line")"
  if [[ -n "$num" ]]; then
    if [[ "$VERBOSE" -eq 1 ]]; then
      echo "Syncing issue #${num} (dry_run=${DRY_RUN})..."
    fi
    if ! state="$(gh api -H "Accept: application/vnd.github+json" "/repos/${REPO}/issues/${num}" --jq '.state')"; then
      echo "Failed to fetch issue #${num} from ${REPO}." >&2
      rm -f "$tmp"
      exit 1
    fi

    if [[ "$state" == "closed" ]]; then
      line="${line/- [ ] /- [x] }"
    else
      if is_checked_line "$line"; then
        if [[ "$DRY_RUN" -eq 0 ]]; then
          if [[ -n "$COMMENT" ]]; then
            gh issue comment "$num" --repo "$REPO" --body "$COMMENT"
          fi
          gh issue close "$num" --repo "$REPO"
        fi
      fi
    fi
  fi
  echo "$line" >> "$tmp"
done < "$FILE"

if [[ "$DRY_RUN" -eq 0 ]]; then
  mv "$tmp" "$FILE"
else
  rm -f "$tmp"
fi
