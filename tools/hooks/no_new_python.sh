#!/usr/bin/env bash
# Claude Code PreToolUse hook. Refuses to create a new .py file in this repo.
# Editing an existing .py file is allowed; the CI ratchet caps its growth.
# See AGENTS.md, section "Flow first".

input="$(cat)"
path="$(printf '%s' "$input" | sed -n 's/.*"file_path"[[:space:]]*:[[:space:]]*"\([^"]*\)".*/\1/p' | head -n 1)"

case "$path" in
  *.py) ;;
  *) exit 0 ;;
esac

case "$path" in
  */third_party/*|*/.lake/*) exit 0 ;;
esac

if [[ -e "$path" ]]; then
  exit 0
fi

echo "Blocked: $path would be a new Python file. New code in this repo is written in Flow. See AGENTS.md, section 'Flow first'." >&2
exit 2
